import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CheckUserMutationTestCase(TestCase):
    """Check user mutation test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )

        self.path = reverse("gql")
        self.query = """
          mutation CheckUser($input: CheckUserInput!) {
            checkUser(input: $input) {
              available
            }
          }
        """

    def tearDown(self):
        self.user.delete()

    def test_user_does_not_exist(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "CheckUser",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": "user.fake",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["checkUser"]["available"])

    def test_user_does_exist(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "CheckUser",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": self.user.username,
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertFalse(data["checkUser"]["available"])
