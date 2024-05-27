import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SigninViewTestCase(TestCase):
    """Signin view test case"""

    def setUp(self):
        self.user = User(username="user", email="user@mail.com")
        self.user.set_password("p455w0rd")
        self.user.save()

        self.path = reverse("pi:v1:accounts:signin")

    def tearDown(self):
        self.user.delete()

    def test_signin(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "username": self.user.username,
                    "password": "p455w0rd",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["token"] is not None)

    def test_signin_wrong_password(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "username": self.user.username,
                    "password": "p455w0rd...",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["errors"][0]["field"], "password")
        self.assertEqual(data["errors"][0]["message"], "Wrong password.")

    def test_signin_tfa(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "username": self.user.username,
                    "password": "p455w0rd",
                    "tfa_code": self.user.get_tfa_code(),
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["token"] is not None)

    def test_signin_tfa_wrong_password(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "username": self.user.username,
                    "password": "p455w0rd...",
                    "tfa_code": self.user.get_tfa_code(),
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["errors"][0]["field"], "password")
        self.assertEqual(data["errors"][0]["message"], "Wrong password.")

    def test_signin_tfa_wrong_tfa_code(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "username": self.user.username,
                    "password": "p455w0rd",
                    "tfa_code": "000000",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["errors"][0]["field"], "tfa_code")
        self.assertEqual(data["errors"][0]["message"], "Wrong TFA authentication code.")
