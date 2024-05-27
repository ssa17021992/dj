from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.common.utils import get_object

User = get_user_model()


class GetObjectTestCase(TestCase):
    """Get object test case"""

    def setUp(self):
        self.user = User(username="user")
        self.user.set_password("p455w0rd")
        self.user.save()
        self.username = self.user.username

    def tearDown(self):
        self.user.delete()

    def test_none(self):
        user = get_object(User, username="user.fake")
        self.assertTrue(user is None)

    def test_success(self):
        user = get_object(User, username=self.username)
        self.assertTrue(user is not None)
        self.assertEqual(user.username, self.username)
