import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class CheckUserViewTestCase(TestCase):
    """Check user view test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )

        self.path = reverse("pi:v1:accounts:check_user")

    def tearDown(self):
        self.user.delete()

    def test_user_does_not_exist(self):
        response = self.client.post(
            self.path,
            json.dumps({"username": "user.fake"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

    def test_user_does_exist(self):
        response = self.client.post(
            self.path,
            json.dumps({"username": self.user.username}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
