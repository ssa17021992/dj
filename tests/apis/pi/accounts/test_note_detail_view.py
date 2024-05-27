import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class NoteDetailViewTestCase(TestCase):
    """Note detail view test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="...", is_superuser=True
        )
        self.note = self.user.notes.create(content="...")

        self.path = reverse(
            "pi:v1:accounts:note_detail",
            kwargs={
                "note_id": self.note.pk,
            },
        )

    def tearDown(self):
        self.note.delete()
        self.user.delete()

    def test_retrieve(self):
        response = self.client.get(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["id"], self.note.pk)

    def test_update(self):
        response = self.client.put(
            self.path,
            json.dumps({"content": "..."}),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)

    def test_partial_update(self):
        response = self.client.patch(
            self.path,
            json.dumps({"content": "..."}),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)

    def test_delete(self):
        response = self.client.delete(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 204)
