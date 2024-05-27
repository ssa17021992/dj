import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth
from apps.accounts.utils import signup_token
from apps.common.utils import to_object

User = get_user_model()


class SignupMutationTestCase(TestCase):
    """Signup mutation test case"""

    def setUp(self):
        self.user = to_object(
            {
                "username": "user",
                "email": "user@mail.com",
                "phone": "5500000000",
            }
        )
        self.token = signup_token(self.user)

        self.path = reverse("gql")
        self.query = """
          mutation Signup($input: SignupInput!) {
            signup(input: $input) {
              user {
                id
                username
                __typename
              }
            }
          }
        """

    def tearDown(self):
        User.objects.filter(username=self.user.username).delete()

    def test_signup(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Signup",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "p455w0rd",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.token),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["signup"]["user"]["username"], self.user.username)

    def test_signup_blank_password(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Signup",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.token),
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "password")
        self.assertEqual(errors[0]["message"], "This field cannot be blank.")
