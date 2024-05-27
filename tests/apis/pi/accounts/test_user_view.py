import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class UserViewTestCase(TestCase):
    """User view test case"""

    def setUp(self):
        self.superuser = User.objects.create(
            username="superuser",
            email="superuser@mail.com",
            password="...",
            is_staff=True,
            is_superuser=True,
        )
        self.users = User.objects.bulk_create(
            [
                User(username=f"user.{x}", email="user@mail.com", password="...")
                for x in range(5)
            ]
        )
        self.username = "user"

        self.path = reverse("pi:v1:accounts:user")

    def tearDown(self):
        for user in self.users:
            user.delete()

        User.objects.filter(username=self.username).delete()
        self.superuser.delete()

    def test_list(self):
        response = self.client.get(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 6)

    def test_create(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "username": self.username,
                    "password": "p455w0rd",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["username"], self.username)
