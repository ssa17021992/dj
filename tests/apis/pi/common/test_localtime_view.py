from django.test import TestCase
from django.urls import reverse


class LocalTimeTestCase(TestCase):
    """Local time test case"""

    def setUp(self):
        self.path = reverse("pi:v1:common:localtime")

    def test_retrieve(self):
        response = self.client.get(self.path, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["localtime"] is not None)
