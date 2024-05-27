import json

from django.test import TestCase
from django.urls import reverse


class FruitsQueryTestCase(TestCase):
    """Fruits query test case"""

    def setUp(self):
        self.path = reverse("gql")
        self.query = """
          query Fruits($first: Int!) {
            fruits(first: $first) {
              edges {
                cursor
                node {
                  id
                  name
                  __typename
                }
              }
            }
          }
        """

    def test_fruits(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Fruits",
                    "query": self.query,
                    "variables": {
                        "first": 10,
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["fruits"]["edges"]), 10)
