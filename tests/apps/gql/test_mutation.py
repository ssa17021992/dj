import graphene
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from apps.gql import mutations


class MutationTestCase(TestCase):
    """Mutation test case."""

    def test_meta_description(self):
        with self.assertRaises(ImproperlyConfigured) as cm:

            class Signin(mutations.Mutation):
                class Meta:
                    pass

        self.assertEqual(str(cm.exception), "description is required.")

    def test_meta_field_name(self):
        with self.assertRaises(ImproperlyConfigured) as cm:

            class Signin(mutations.Mutation):
                class Meta:
                    description = "Signin."

        self.assertEqual(str(cm.exception), "field_name is required.")

    def test_meta_field_type(self):
        with self.assertRaises(ImproperlyConfigured) as cm:

            class Signin(mutations.Mutation):
                class Meta:
                    description = "Signin."
                    field_name = "token"

        self.assertEqual(str(cm.exception), "field_type is required.")

    def test_meta_properly_configured(self):
        class Signin(mutations.Mutation):
            class Meta:
                description = "Signin."
                field_name = "token"
                field_type = graphene.String

        meta_opts = Signin._meta
        self.assertEqual(meta_opts.description, "Signin.")
        self.assertEqual(meta_opts.field_name, "token")
        self.assertEqual(meta_opts.field_type, graphene.String)
