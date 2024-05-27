import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class NoteViewTestCase(TestCase):
    """Note view test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="...", is_superuser=True
        )
        self.notes = self.user.notes.bulk_create(
            [self.user.notes.model(user=self.user, content="...") for _ in range(5)]
        )

        self.path = reverse("pi:v1:accounts:note")

    def tearDown(self):
        for note in self.notes:
            note.delete()

        self.user.delete()

    def test_list(self):
        response = self.client.get(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["results"]), 5)

    def test_create(self):
        response = self.client.post(
            self.path,
            json.dumps({"content": "..."}),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["content"], "...")
