from django.test import TestCase
from django.urls import reverse

from apis.auth import TokenAuth
from apps.accounts.utils import signup_token
from apps.common.utils import to_object


class CheckSignupTokenViewTestCase(TestCase):
    """Check signup token view test case"""

    def setUp(self):
        self.user = to_object(
            {
                "username": "user",
                "email": "user@mail.com",
                "phone": "5500000000",
            }
        )
        self.token = signup_token(self.user)

        self.path = reverse("pi:v1:accounts:check_signup_token")

    def test_signup_token(self):
        response = self.client.post(
            self.path,
            content_type="application/json",
            HTTP_AUTHORIZATION="%s %s" % (TokenAuth.keyword, self.token),
        )

        self.assertEqual(response.status_code, 200)
