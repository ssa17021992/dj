import json

from django.test import TestCase
from django.urls import reverse


class CreateCommentMutationTestCase(TestCase):
    """Create comment mutation test case"""

    def setUp(self):
        self.path = reverse("gql")
        self.query = """
          mutation CreateComment($input: CreateCommentInput!) {
            createComment(input: $input) {
              comment {
                id
                content
                user {
                  id
                  firstName
                  lastName
                  email
                  __typename
                }
                __typename
              }
            }
          }
        """

    def test_create_comment(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "CreateComment",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "content": "...",
                            "user": {
                                "firstName": "User",
                                "lastName": "User",
                                "email": "user@mail.com",
                            },
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["createComment"]["comment"]["content"], "...")
        self.assertEqual(
            data["createComment"]["comment"]["user"]["email"], "user@mail.com"
        )
