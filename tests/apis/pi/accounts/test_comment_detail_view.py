import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Note

User = get_user_model()


class CommentDetailViewTestCase(TestCase):
    """Comment detail view test case"""

    def setUp(self):
        self.comment = Note.objects.create(
            content="...", user=User.objects.create(username="user", password="...")
        )

        self.path = reverse(
            "pi:v1:accounts:comment_detail",
            kwargs={
                "comment_id": self.comment.pk,
            },
        )

    def tearDown(self):
        self.comment.delete()
        self.comment.user.delete()

    def test_retrieve(self):
        response = self.client.get(self.path, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.comment.pk)

    def test_update(self):
        response = self.client.put(
            self.path,
            json.dumps(
                {
                    "content": "...",
                    "user": {
                        "email": "user@mail.com",
                        "first_name": "",
                        "last_name": "",
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)

    def test_partial_update(self):
        response = self.client.patch(
            self.path, json.dumps({"content": "..."}), content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.delete(self.path, content_type="application/json")

        self.assertEqual(response.status_code, 204)
