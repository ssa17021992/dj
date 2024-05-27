import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class MeViewTestCase(TestCase):
    """Me view test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )

        self.path = reverse("pi:v1:accounts:me")

    def tearDown(self):
        self.user.delete()

    def test_retrieve(self):
        response = self.client.get(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], self.user.username)

    def test_partial_update(self):
        response = self.client.patch(
            self.path,
            json.dumps(
                {
                    "first_name": "User",
                    "middle_name": "User",
                    "last_name": "User",
                    "phone": "5500000000",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
