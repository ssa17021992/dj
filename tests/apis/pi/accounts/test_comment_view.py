import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Note

User = get_user_model()


class CommentViewTestCase(TestCase):
    """Comment view test case"""

    def setUp(self):
        self.comments = [
            Note(content="...", user=User(username=f"user.{x}", password="..."))
            for x in range(5)
        ]
        User.objects.bulk_create([comment.user for comment in self.comments])
        Note.objects.bulk_create(self.comments)

        self.path = reverse("pi:v1:accounts:comment")

    def tearDown(self):
        for comment in self.comments:
            comment.delete()
            comment.user.delete()

    def test_list(self):
        response = self.client.get(self.path, content_type="application/json")

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 5)

    def test_create(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "content": "...",
                    "user": {
                        "email": "user@mail.com",
                        "first_name": "...",
                        "last_name": "...",
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["content"], "...")
        self.assertEqual(data["user"]["email"], "user@mail.com")
