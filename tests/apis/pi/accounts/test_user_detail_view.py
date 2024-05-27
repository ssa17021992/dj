import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class UserDetailViewTestCase(TestCase):
    """User detail view test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )
        self.superuser = User.objects.create(
            username="superuser",
            email="superuser@mail.com",
            password="...",
            is_staff=True,
            is_superuser=True,
        )

        self.path = reverse(
            "pi:v1:accounts:user_detail",
            kwargs={
                "user_id": self.user.pk,
            },
        )

    def tearDown(self):
        self.user.delete()
        self.superuser.delete()

    def test_retrieve(self):
        response = self.client.get(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["username"], self.user.username)

    def test_update(self):
        response = self.client.put(
            self.path,
            json.dumps(
                {
                    "first_name": "...",
                    "middle_name": "...",
                    "last_name": "...",
                    "birthday": "1980-04-10",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 200)

    def test_partial_update(self):
        response = self.client.patch(
            self.path,
            json.dumps({"first_name": "..."}),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.delete(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 204)
