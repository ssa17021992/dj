import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class CreateUserMutationTestCase(TestCase):
    """Create user mutation test case"""

    def setUp(self):
        self.superuser = User.objects.create(
            username="superuser",
            email="superuser@mail.com",
            password="...",
            is_staff=True,
            is_superuser=True,
        )
        self.username = "user"

        self.path = reverse("gql")
        self.query = """
          mutation CreateUser($input: CreateUserInput!) {
            createUser(input: $input) {
              user {
                id
                username
                __typename
              }
            }
          }
        """

    def tearDown(self):
        User.objects.filter(username=self.username).delete()
        self.superuser.delete()

    def test_create_user(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "CreateUser",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": self.username,
                            "password": "p455w0rd",
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
        self.assertEqual(data["createUser"]["user"]["username"], "user")
