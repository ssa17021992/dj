from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class RefreshTokenViewTestCase(TestCase):
    """Refresh token view test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )

        self.path = reverse("pi:v1:accounts:refresh_token")

    def tearDown(self):
        self.user.delete()

    def test_refresh_token(self):
        response = self.client.post(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.user.get_refresh_token()),
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["token"] is not None)
        self.assertEqual(len(data["token"].split(".")), 3)
