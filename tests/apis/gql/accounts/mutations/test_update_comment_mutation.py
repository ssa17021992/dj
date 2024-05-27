import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.gql.utils import to_global_id

User = get_user_model()


class UpdateCommentMutationTestCase(TestCase):
    """Update comment mutation test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )
        self.user_id = to_global_id("Person", self.user.pk)
        self.comment = self.user.notes.create(content="...")
        self.comment_id = to_global_id("Comment", self.comment.pk)

        self.path = reverse("gql")
        self.query = """
          mutation UpdateComment($id: ID!, $input: UpdateCommentInput!) {
            updateComment(id: $id, input: $input) {
              comment {
                id
                content
                user {
                  id
                  email
                  __typename
                }
                __typename
              }
            }
          }
        """

    def tearDown(self):
        self.comment.delete()
        self.user.delete()

    def test_update_comment(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "UpdateComment",
                    "query": self.query,
                    "variables": {
                        "id": self.comment_id,
                        "input": {
                            "content": "new...",
                            "user": {
                                "email": "user.new@mail.com",
                            },
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["updateComment"]["comment"]["id"], self.comment_id)
        self.assertEqual(data["updateComment"]["comment"]["content"], "new...")
        self.assertEqual(data["updateComment"]["comment"]["user"]["id"], self.user_id)
        self.assertEqual(
            data["updateComment"]["comment"]["user"]["email"], "user.new@mail.com"
        )
