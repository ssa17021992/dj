import json

from django.test import TestCase
from django.urls import reverse


class EchoTestCase(TestCase):
    """Echo test case"""

    def setUp(self):
        self.path = reverse("pi:v1:common:echo")

    def test_echo(self):
        response = self.client.post(
            self.path, json.dumps({"message": "..."}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["message"], "...")
