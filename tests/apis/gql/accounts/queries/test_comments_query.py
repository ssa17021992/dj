import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import Note

User = get_user_model()


class CommentsQueryTestCase(TestCase):
    """Comments query test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )
        self.comments = Note.objects.bulk_create(
            [Note(user=self.user, content="...") for _ in range(5)]
        )

        self.path = reverse("gql")
        self.query = """
          query Comments($first: Int!) {
            comments(first: $first) {
              edges {
                cursor
                node {
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
          }
        """

    def tearDown(self):
        for comment in self.comments:
            comment.delete()

        self.user.delete()

    def test_comments(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Comments",
                    "query": self.query,
                    "variables": {
                        "first": 5,
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["comments"]["edges"]), 5)
