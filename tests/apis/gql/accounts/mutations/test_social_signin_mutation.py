import json
from hashlib import md5

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SocialSigninMutationTestCase(TestCase):
    """Social signin mutation test case"""

    def setUp(self):
        self.token = "123"
        self.username = f"dummy.{md5(self.token.encode()).hexdigest()}"

        self.path = reverse("gql")
        self.query = """
          mutation SocialSignin($input: SocialSigninInput!) {
            socialSignin(input: $input) {
              token
              user {
                id
                username
                __typename
              }
            }
          }
        """

    def tearDown(self):
        if hasattr(self, "user"):
            self.user.delete()

    def test_social_signin_tfa_dummy(self):
        self.user = User.objects.create(
            username=self.username, email="dummy@mail.com", password="..."
        )
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "SocialSignin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "social": "DUMMY",
                            "token": self.token,
                            "tfaCode": self.user.get_tfa_code(),
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["socialSignin"]["token"] is not None)

    def test_social_signin_tfa_dummy_wrong_tfa_code(self):
        self.user = User.objects.create(
            username=self.username, email="dummy@mail.com", password="..."
        )
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "SocialSignin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "social": "DUMMY",
                            "token": self.token,
                            "tfaCode": "000000",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "tfaCode")
        self.assertEqual(errors[0]["message"], "Wrong TFA authentication code.")

    def test_social_signin_dummy(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "SocialSignin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "social": "DUMMY",
                            "token": self.token,
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["socialSignin"]["token"] is not None)

    def test_social_signin_dummy_no_token(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "SocialSignin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "social": "DUMMY",
                            "token": "",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "token")
        self.assertEqual(errors[0]["message"], "This field is required.")
