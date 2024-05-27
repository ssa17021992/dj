import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.gql.utils import to_global_id

User = get_user_model()


class CommentQueryTestCase(TestCase):
    """Comment query test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )
        self.comment = self.user.notes.create(content="...")
        self.comment_id = to_global_id("Comment", self.comment.pk)

        self.path = reverse("gql")
        self.query = """
          query Comment($id: ID!) {
            comment(id: $id) {
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
        """

    def tearDown(self):
        self.comment.delete()
        self.user.delete()

    def test_comment(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Comment",
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
        self.assertEqual(data["comment"]["id"], self.comment_id)
