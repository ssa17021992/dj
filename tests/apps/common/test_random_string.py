from django.test import TestCase

from apps.common.utils import default_chars, random_string


class RandomStringTestCase(TestCase):
    """Random string test case"""

    def test_default_length(self):
        id = random_string()
        self.assertEqual(len(id), 20)

    def test_default_chars(self):
        id = random_string()
        for char in id:
            self.assertTrue(char in default_chars)

    def test_custom_length(self):
        id = random_string(length=10)
        self.assertEqual(len(id), 10)

    def test_custom_chars(self):
        custom_chars = "01223456789"
        id = random_string(chars=custom_chars)
        for char in id:
            self.assertTrue(char in custom_chars)
