import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.gql.utils import to_global_id

User = get_user_model()


class DeleteCommentMutationTestCase(TestCase):
    """Delete comment mutation test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )
        self.user_id = to_global_id("Person", self.user.pk)
        self.comment = self.user.notes.create(content="...")
        self.comment_id = to_global_id("Comment", self.comment.pk)

        self.path = reverse("gql")
        self.query = """
          mutation DeleteComment($id: ID!) {
            deleteComment(id: $id) {
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

    def test_delete_comment(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "DeleteComment",
                    "query": self.query,
                    "variables": {
                        "id": self.comment_id,
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["deleteComment"]["comment"]["id"], self.comment_id)
        self.assertEqual(data["deleteComment"]["comment"]["user"]["id"], self.user_id)
