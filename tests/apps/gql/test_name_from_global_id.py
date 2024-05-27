from django.test import TestCase

from apps.gql.utils import name_from_global_id, to_global_id


class NameFromGlobalIdTestCase(TestCase):
    """Name from global id test case."""

    def test_name_from_global_id(self):
        global_id = to_global_id("User", "1")
        type_name = name_from_global_id(global_id)
        self.assertEqual(type_name, "User")
