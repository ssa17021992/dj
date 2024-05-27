import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class UsersQueryTestCase(TestCase):
    """Users query test case"""

    def setUp(self):
        self.superuser = User.objects.create(
            username="superuser",
            email="superuser@mail.com",
            password="...",
            is_staff=True,
            is_superuser=True,
        )
        self.users = User.objects.bulk_create(
            [User(username=f"user.{x}", password="...") for x in range(5)]
        )

        self.path = reverse("gql")
        self.query = """
          query Users($first: Int!, $search: String) {
            users(first: $first, search: $search) {
              edges {
                cursor
                node {
                  id
                  username
                  __typename
                }
              }
            }
          }
        """

    def tearDown(self):
        for user in self.users:
            user.delete()

        self.superuser.delete()

    def test_users(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Users",
                    "query": self.query,
                    "variables": {
                        "first": 5,
                        "search": "user.",
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["users"]["edges"]), 5)
