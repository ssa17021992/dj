import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth
from apps.accounts.models import Note
from apps.gql.utils import to_global_id

User = get_user_model()


class UserNotesQueryTestCase(TestCase):
    """User notes query test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )
        self.user_id = to_global_id("User", self.user.pk)
        self.notes = Note.objects.bulk_create(
            [Note(user=self.user, content="...") for _ in range(5)]
        )
        self.superuser = User.objects.create(
            username="superuser",
            email="superuser@mail.com",
            password="...",
            is_staff=True,
            is_superuser=True,
        )

        self.path = reverse("gql")
        self.query = """
          query UserNotes($first: Int!, $userId: ID, $username: String) {
            userNotes(
              first: $first, userId: $userId, username: $username
            ) {
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
        self.superuser.delete()

    def test_notes_by_user_id(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "UserNotes",
                    "query": self.query,
                    "variables": {
                        "first": 5,
                        "userId": self.user_id,
                        "username": None,
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["userNotes"]["edges"]), 5)

    def test_notes_by_username(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "UserNotes",
                    "query": self.query,
                    "variables": {
                        "first": 5,
                        "userId": None,
                        "username": self.user.username,
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["userNotes"]["edges"]), 5)
