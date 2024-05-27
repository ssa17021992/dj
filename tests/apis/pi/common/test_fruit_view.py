from django.test import TestCase
from django.urls import reverse


class FruitViewTestCase(TestCase):
    """Fruit view test case"""

    def setUp(self):
        self.path = reverse("pi:v1:common:fruit")

    def test_list(self):
        response = self.client.get(self.path, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 10)
