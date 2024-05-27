from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth

User = get_user_model()


class CheckPasswordTokenViewTestCase(TestCase):
    """Check password token view test case"""

    def setUp(self):
        self.user = User.objects.create(
            username="user", email="user@mail.com", password="..."
        )

        self.path = reverse("pi:v1:accounts:check_password_token")

    def tearDown(self):
        self.user.delete()

    def test_check_password_token(self):
        response = self.client.post(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s"
            % (TokenAuth.keyword, self.user.get_passwd_token()),
        )

        self.assertEqual(response.status_code, 200)
