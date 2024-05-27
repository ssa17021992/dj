import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class EnableTFAMutationTestCase(TestCase):
    """EnableTFA mutation test case"""

    def setUp(self):
        self.user = User(username="user", email="user@mail.com")
        self.user.set_password("p455w0rd")
        self.user.save()

        self.path = reverse("gql")
        self.query = """
          mutation EnableTFA($input: EnableTFAInput!) {
            enableTFA(input: $input) {
              tfaSecret
              user {
                id
                username
                tfaActive
                __typename
              }
            }
          }
        """

    def tearDown(self):
        self.user.delete()

    def test_enable_tfa(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "EnableTFA",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "p455w0rd",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["enableTFA"]["tfaSecret"]), 32)
        self.assertTrue(data["enableTFA"]["user"]["tfaActive"])

    def test_enable_tfa_wrong_password(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "EnableTFA",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "p455w0rd...",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "password")
        self.assertEqual(errors[0]["message"], "Wrong password.")

    def test_enable_tfa_is_already_enabled(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "EnableTFA",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "p455w0rd",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "tfaSecret")
        self.assertEqual(
            errors[0]["message"], "The TFA authentication is already enabled."
        )
