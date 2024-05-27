import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class CreateNoteMutationTestCase(TestCase):
    """Create note mutation test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )

        self.path = reverse("gql")
        self.query = """
          mutation CreateNote($input: CreateNoteInput!) {
            createNote(input: $input) {
              note {
                id
                content
                __typename
              }
            }
          }
        """

    def tearDown(self):
        self.user.delete()

    def test_create_note(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "CreateNote",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "content": "...",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["createNote"]["note"]["content"], "...")
