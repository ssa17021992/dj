import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class MeQueryTestCase(TestCase):
    """Me query test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )

        self.path = reverse("gql")
        self.query = """
          query Me {
            me {
              id
              username
              __typename
            }
          }
        """

    def tearDown(self):
        self.user.delete()

    def test_me(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Me",
                    "query": self.query,
                    "variables": None,
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(data["me"]["username"], self.user.username)
