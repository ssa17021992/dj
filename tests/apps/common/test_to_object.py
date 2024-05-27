from django.test import TestCase

from apps.common.utils import to_object


class ToObjectTestCase(TestCase):
    """To object test case"""

    def test_dict_to_object(self):
        obj = to_object(
            {
                "pi": 3.14,
            }
        )
        self.assertTrue(hasattr(obj, "pi"))

    def test_output_class_name(self):
        obj = to_object({})
        self.assertEqual(type(obj).__name__, "o")

    def test_int_to_object(self):
        obj = to_object(1)
        self.assertTrue(isinstance(obj, int))

    def test_none_to_object(self):
        obj = to_object(None)
        self.assertTrue(obj is None)

    def test_null_list_to_object(self):
        obj = to_object([])
        self.assertTrue(isinstance(obj, list))
        self.assertEqual(len(obj), 0)

    def test_list_of_dicts_to_object(self):
        obj = to_object(
            [
                {},
                {},
            ]
        )
        self.assertTrue(isinstance(obj, list))
        self.assertEqual(len(obj), 2)
        self.assertEqual(type(obj[0]).__name__, "o")
        self.assertEqual(type(obj[1]).__name__, "o")
