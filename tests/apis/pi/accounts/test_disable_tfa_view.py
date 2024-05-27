import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class DisableTFAViewTestCase(TestCase):
    """Disable TFA view test case"""

    def setUp(self):
        self.user = User(username="user", email="user@mail.com")
        self.user.set_password("p455w0rd")
        self.user.save()

        self.path = reverse("pi:v1:accounts:disable_tfa")

    def tearDown(self):
        self.user.delete()

    def test_disable_tfa(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "password": "p455w0rd",
                    "tfa_code": self.user.get_tfa_code(),
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data["tfa_secret"]), 0)
        self.assertFalse(data["user"]["tfa_active"])

    def test_disable_tfa_is_not_enabled(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "password": "p455w0rd",
                    "tfa_code": self.user.get_tfa_code(),
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["errors"][0]["field"], "tfa_secret")
        self.assertEqual(
            data["errors"][0]["message"], "The TFA authentication is not enabled."
        )

    def test_disable_tfa_wrong_password(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "password": "p455w0rd...",
                    "tfa_code": self.user.get_tfa_code(),
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["errors"][0]["field"], "password")
        self.assertEqual(data["errors"][0]["message"], "Wrong password.")

    def test_disable_tfa_wrong_tfa_code(self):
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "password": "p455w0rd",
                    "tfa_code": "000000",
                }
            ),
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.user.get_token()),
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["errors"][0]["field"], "tfa_code")
        self.assertEqual(data["errors"][0]["message"], "Wrong TFA authentication code.")
