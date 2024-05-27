from django.core.exceptions import ValidationError
from django.test import TestCase

from apps.gql.utils import validation_error_to_error_list


class ValidationErrorToErrorListTestCase(TestCase):
    """Validation error to error list test case."""

    def test_validation_error_to_error_list_string(self):
        error_list = validation_error_to_error_list(ValidationError("Wrong password."))
        self.assertEqual(len(error_list), 1)
        self.assertTrue(None in [error["field"] for error in error_list])
        self.assertTrue("Wrong password." in [error["message"] for error in error_list])

    def test_validation_error_to_error_list_dict(self):
        error_list = validation_error_to_error_list(
            ValidationError({"password": "Wrong password."})
        )
        self.assertEqual(len(error_list), 1)
        self.assertTrue("password" in [error["field"] for error in error_list])
        self.assertTrue("Wrong password." in [error["message"] for error in error_list])

    def test_validation_error_to_error_list_code(self):
        error_list = validation_error_to_error_list(
            ValidationError("Wrong password.", code="password")
        )
        self.assertEqual(len(error_list), 1)
        self.assertTrue("password" in [error["field"] for error in error_list])
        self.assertTrue("Wrong password." in [error["message"] for error in error_list])
