import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class ResetPasswordMutationTestCase(TestCase):
    """Reset password mutation test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )

        self.path = reverse("gql")
        self.query = """
          mutation ResetPassword($input: ResetPasswordInput!) {
            resetPassword(input: $input) {
              success
            }
          }
        """

    def tearDown(self):
        self.user.delete()

    def test_reset_password(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "ResetPassword",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "p455w0rd",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.user.get_passwd_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["resetPassword"]["success"])
