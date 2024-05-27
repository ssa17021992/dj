import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth
from apps.gql.utils import to_global_id

User = get_user_model()


class UpdateUserMutationTestCase(TestCase):
    """Update user mutation test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )
        self.user_id = to_global_id("User", self.user.pk)
        self.superuser = User.objects.create(
            username="superuser",
            email="superuser@mail.com",
            password="...",
            is_staff=True,
            is_superuser=True,
        )

        self.path = reverse("gql")
        self.query = """
          mutation UpdateUser($id: ID!, $input: UpdateUserInput!) {
            updateUser(id: $id, input: $input) {
              user {
                id
                username
                email
                __typename
              }
            }
          }
        """

    def tearDown(self):
        self.user.delete()
        self.superuser.delete()

    def test_update_user(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "UpdateUser",
                    "query": self.query,
                    "variables": {
                        "id": self.user_id,
                        "input": {
                            "email": "user.new@mail.com",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.superuser.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["updateUser"]["user"]["email"], "user.new@mail.com")
