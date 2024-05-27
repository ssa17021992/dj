from django.test import TestCase

from apps.common.utils import unique_id


class UniqueIdTestCase(TestCase):
    """Unique id test case"""

    def test_default_length(self):
        uid = unique_id()
        self.assertEqual(len(uid), 22)

    def test_custom_length(self):
        uid = unique_id(length=11)
        self.assertEqual(len(uid), 11)

    def test_zero_length(self):
        uid = unique_id(length=0)
        self.assertEqual(len(uid), 0)

    def test_big_length(self):
        uid = unique_id(length=1000)
        self.assertEqual(len(uid), 1000)
