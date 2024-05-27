import json

from django.test import TestCase
from django.urls import reverse


class SendSignupTokenViewTestCase(TestCase):
    """Send signup token view test case"""

    def setUp(self):
        self.path = reverse("pi:v1:accounts:send_signup_token")

    def test_signup_token(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "username": "user",
                    "email": "user@mail.com",
                    "phone": "5500000000",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
