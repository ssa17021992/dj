from django.test import TestCase

from apps.common.models import Model


class ModelTestCase(TestCase):
    """Model test case"""

    def test_attributes(self):
        self.assertTrue(hasattr(Model, "_meta"))
        self.assertTrue(hasattr(Model._meta, "fields"))
        self.assertTrue("id" in [f.name for f in Model._meta.fields])
        self.assertTrue(Model._meta.abstract)
