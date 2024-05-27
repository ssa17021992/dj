import json

from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth
from apps.accounts.utils import signup_token
from apps.common.utils import to_object


class CheckSignupTokenMutationTestCase(TestCase):
    """Check signup token mutation test case"""

    def setUp(self):
        self.token = signup_token(
            to_object(
                {
                    "username": "user",
                    "email": "user@mail.com",
                    "phone": None,
                }
            )
        )

        self.path = reverse("gql")
        self.query = """
          mutation CheckSignupToken {
            checkSignupToken {
              success
            }
          }
        """

    def test_check_signup_token(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "CheckSignupToken",
                    "query": self.query,
                    "variables": None,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.token),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["checkSignupToken"]["success"])

    def test_no_token(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "CheckSignupToken",
                    "query": self.query,
                    "variables": None,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "auth")
        self.assertEqual(errors[0]["message"], "The token was not provided.")
