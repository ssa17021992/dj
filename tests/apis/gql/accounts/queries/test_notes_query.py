import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth
from apps.accounts.models import Note

User = get_user_model()


class NotesQueryTestCase(TestCase):
    """Notes query test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )
        self.notes = Note.objects.bulk_create(
            [Note(user=self.user, content="...") for _ in range(5)]
        )

        self.path = reverse("gql")
        self.query = """
          query Notes($first: Int!) {
            notes(first: $first) {
              edges {
                cursor
                node {
                  id
                  content
                  __typename
                }
              }
            }
          }
        """

    def tearDown(self):
        for note in self.notes:
            note.delete()

        self.user.delete()

    def test_notes(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Notes",
                    "query": self.query,
                    "variables": {
                        "first": 5,
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["notes"]["edges"]), 5)
