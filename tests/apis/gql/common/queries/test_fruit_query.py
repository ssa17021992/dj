import json

from django.test import TestCase
from django.urls import reverse

from apps.common.utils import unique_id
from apps.gql.utils import to_global_id


class FruitQueryTestCase(TestCase):
    """Fruit query test case"""

    def setUp(self):
        self.fruit_id = to_global_id("Fruit", unique_id())

        self.path = reverse("gql")
        self.query = """
          query Fruit($id: ID!) {
            fruit(id: $id) {
              id
              name
              __typename
            }
          }
        """

    def test_fruit(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Fruit",
                    "query": self.query,
                    "variables": {
                        "id": self.fruit_id,
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["fruit"], None)
