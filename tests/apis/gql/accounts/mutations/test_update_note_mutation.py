import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth
from apps.gql.utils import to_global_id

User = get_user_model()


class UpdateNoteMutationTestCase(TestCase):
    """Update note mutation test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )
        self.note = self.user.notes.create(content="...")
        self.note_id = to_global_id("Note", self.note.pk)

        self.path = reverse("gql")
        self.query = """
          mutation UpdateNote($id: ID!, $input: UpdateNoteInput!) {
            updateNote(id: $id, input: $input) {
              note {
                id
                content
                __typename
              }
            }
          }
        """

    def tearDown(self):
        self.note.delete()
        self.user.delete()

    def test_update_note(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "UpdateNote",
                    "query": self.query,
                    "variables": {
                        "id": self.note_id,
                        "input": {
                            "content": "new...",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["updateNote"]["note"]["content"], "new...")
