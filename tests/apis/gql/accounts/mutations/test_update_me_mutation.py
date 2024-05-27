import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class UpdateMeMutationTestCase(TestCase):
    """Update me mutation test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )

        self.path = reverse("gql")
        self.query = """
          mutation UpdateMe($input: UpdateMeInput!) {
            updateMe(input: $input) {
              me {
                id
                firstName
                middleName
                lastName
                __typename
              }
            }
          }
        """

    def tearDown(self):
        self.user.delete()

    def test_update_me(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "UpdateMe",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "firstName": "User.new",
                            "middleName": "User.new",
                            "lastName": "User.new",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["updateMe"]["me"]["firstName"], "User.new")
        self.assertEqual(data["updateMe"]["me"]["middleName"], "User.new")
        self.assertEqual(data["updateMe"]["me"]["lastName"], "User.new")
