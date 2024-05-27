import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SigninMutationTestCase(TestCase):
    """Signin mutation test case"""

    def setUp(self):
        self.user = User(username="user", email="user@mail.com")
        self.user.set_password("p455w0rd")
        self.user.save()

        self.path = reverse("gql")
        self.query = """
          mutation Signin($input: SigninInput!) {
            signin(input: $input) {
              token
              user {
                id
                username
                __typename
              }
            }
          }
        """

    def tearDown(self):
        self.user.delete()

    def test_signin(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Signin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": self.user.username,
                            "password": "p455w0rd",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["signin"]["token"] is not None)
        self.assertEqual(data["signin"]["user"]["username"], self.user.username)

    def test_signin_wrong_password(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Signin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": self.user.username,
                            "password": "password...",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "password")
        self.assertEqual(errors[0]["message"], "Wrong password.")

    def test_signin_user_does_not_exist(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Signin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": "user.fake",
                            "password": "p455w0rd",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "username")
        self.assertEqual(errors[0]["message"], "User does not exist.")

    def test_signin_tfa(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Signin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": self.user.username,
                            "password": "p455w0rd",
                            "tfaCode": self.user.get_tfa_code(),
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()["data"]
        self.assertTrue(data["signin"]["token"] is not None)
        self.assertEqual(data["signin"]["user"]["username"], self.user.username)

    def test_signin_tfa_wrong_password(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Signin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": self.user.username,
                            "password": "p455w0rd...",
                            "tfaCode": self.user.get_tfa_code(),
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "password")
        self.assertEqual(errors[0]["message"], "Wrong password.")

    def test_signin_tfa_wrong_tfa_code(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "operationName": "Signin",
                    "query": self.query,
                    "variables": {
                        "input": {
                            "username": self.user.username,
                            "password": "p455w0rd",
                            "tfaCode": "000000",
                        },
                    },
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        errors = response.json()["errors"]
        self.assertEqual(errors[0]["field"], "tfaCode")
        self.assertEqual(errors[0]["message"], "Wrong TFA authentication code.")
