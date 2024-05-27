import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class DisableTFAMutationTestCase(TestCase):
    """DisableTFA mutation test case"""

    def setUp(self):
        self.user = User(username="user", email="user@mail.com")
        self.user.set_password("p455w0rd")
        self.user.save()

        self.path = reverse("gql")
        self.query = """
          mutation DisableTFA($input: DisableTFAInput!) {
            disableTFA(input: $input) {
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

    def test_disable_tfa(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "DisableTFA",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "p455w0rd",
                            "tfaCode": self.user.get_tfa_code(),
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertEqual(len(data["disableTFA"]["tfaSecret"]), 0)
        self.assertFalse(data["disableTFA"]["user"]["tfaActive"])

    def test_disable_tfa_wrong_password(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "DisableTFA",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "p455w0rd...",
                            "tfaCode": self.user.get_tfa_code(),
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

    def test_disable_tfa_wrong_tfa_code(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "DisableTFA",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "p455w0rd",
                            "tfaCode": "000000",
                        },
                    },
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "tfaCode")
        self.assertEqual(errors[0]["message"], "Wrong TFA authentication code.")

    def test_disable_tfa_is_not_enabled(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "DisableTFA",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "password": "p455w0rd",
                            "tfaCode": self.user.get_tfa_code(),
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
        self.assertEqual(errors[0]["message"], "The TFA authentication is not enabled.")
