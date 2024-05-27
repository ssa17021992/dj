from django.test import TestCase

from apps.gql.utils import id_from_global_id, to_global_id


class IdFromGlobalIdTestCase(TestCase):
    """Id from global id test case."""

    def test_id_from_global_id(self):
        global_id = to_global_id("User", "1")
        id = id_from_global_id(global_id)
        self.assertEqual(id, "1")
