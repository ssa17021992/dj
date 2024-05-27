import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class ChangePasswordMutationTestCase(TestCase):
    """Change password mutation test case"""

    def setUp(self):
        self.user = User(username="user", email="user@mail.com")
        self.user.set_password("p455w0rd")
        self.user.save()

        self.path = reverse("gql")
        self.query = """
          mutation ChangePassword($input: ChangePasswordInput!) {
            changePassword(input: $input) {
              success
            }
          }
        """

    def tearDown(self):
        self.user.delete()

    def test_change_password(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "ChangePassword",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "current": "p455w0rd",
                            "password": "12345678",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["changePassword"]["success"])
