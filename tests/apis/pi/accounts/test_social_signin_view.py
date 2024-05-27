import json
from hashlib import md5

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class SocialSigninViewTestCase(TestCase):
    """Social signin view test case"""

    def setUp(self):
        self.token = "123"
        self.username = f"dummy.{md5(self.token.encode()).hexdigest()}"

        self.path = reverse("pi:v1:accounts:social_signin")

    def tearDown(self):
        if hasattr(self, "user"):
            self.user.delete()

    def test_social_signin_dummy(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "social": "dummy",
                    "token": self.token,
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["token"] is not None)

    def test_social_signin_dummy_wrong_token(self):
        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "social": "dummy",
                    "token": "",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["errors"][0]["field"], "token")
        self.assertEqual(data["errors"][0]["message"], "This field may not be blank.")

    def test_social_signin_tfa_dummy(self):
        self.user = User.objects.create(
            username=self.username, email="dummy@mail.com", password="..."
        )
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "social": "dummy",
                    "token": self.token,
                    "tfa_code": self.user.get_tfa_code(),
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["token"] is not None)

    def test_social_signin_tfa_dummy_wrong_tfa_code(self):
        self.user = User.objects.create(
            username=self.username, email="dummy@mail.com", password="..."
        )
        self.user.enable_tfa()

        response = self.client.post(
            self.path,
            json.dumps(
                {
                    "social": "dummy",
                    "token": self.token,
                    "tfa_code": "000000",
                }
            ),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data["errors"][0]["field"], "tfa_code")
        self.assertEqual(data["errors"][0]["message"], "Wrong TFA authentication code.")
