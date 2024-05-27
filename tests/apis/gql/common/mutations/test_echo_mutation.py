import json

from django.test import TestCase
from django.urls import reverse


class EchoMutationTestCase(TestCase):
    """Echo mutation test case"""

    def setUp(self):
        self.path = reverse("gql")
        self.query = """
          mutation Echo($message: String!) {
            echo(message: $message) {
              message
              __typename
            }
          }
        """

    def test_echo(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Echo",
                    "query": self.query,
                    "variables": {
                        "message": "...",
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["echo"]["message"], "...")
