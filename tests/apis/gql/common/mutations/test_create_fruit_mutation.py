import json

from django.test import TestCase
from django.urls import reverse


class CreateFruitMutationTestCase(TestCase):
    """Create fruit mutation test case"""

    def setUp(self):
        self.path = reverse("gql")
        self.query = """
          mutation CreateFruit($input: CreateFruitInput!) {
            createFruit(input: $input) {
              fruit {
                id
                name
                type
                created
                __typename
              }
            }
          }
        """

    def test_create_phone(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "CreateFruit",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "name": "Orange",
                            "type": "CITRUS",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["createFruit"]["fruit"]["name"], "Orange")
        self.assertEqual(data["createFruit"]["fruit"]["type"], "CITRUS")
