import json

from django.test import TestCase
from django.urls import reverse


class LocaltimeQueryTestCase(TestCase):
    """Localtime test case"""

    def setUp(self):
        self.path = reverse("gql")
        self.query = """
          query Localtime {
            localtime {
              now
              __typename
            }
          }
        """

    def test_localtime(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Localtime",
                    "query": self.query,
                    "variables": None,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["localtime"]["now"] is not None)
