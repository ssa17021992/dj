import json

from django.test import TestCase
from django.urls import reverse


class SendSignupTokenMutationTestCase(TestCase):
    """Send signup token mutation test case"""

    def setUp(self):
        self.path = reverse("gql")
        self.query = """
          mutation SendSignupToken($input: SignupTokenInput!) {
            sendSignupToken(input: $input) {
              success
            }
          }
        """

    def test_send_signup_token(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "SendSignupToken",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": "user",
                            "email": "user@mail.com",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["sendSignupToken"]["success"])
