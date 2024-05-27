from django.test import TestCase

from apps.cors.conf import conf


class ConfTestCase(TestCase):
    """Conf test case"""

    def setUp(self):
        self.conf = conf

    def tearDown(self):
        self.conf = None

    def test_cors_origin_allow_all(self):
        self.assertTrue(hasattr(self.conf, "CORS_ORIGIN_ALLOW_ALL"))
        self.assertEqual(type(self.conf.CORS_ORIGIN_ALLOW_ALL), bool)

    def test_cors_allow_credentials(self):
        self.assertTrue(hasattr(self.conf, "CORS_ALLOW_CREDENTIALS"))
        self.assertEqual(type(self.conf.CORS_ALLOW_CREDENTIALS), bool)

    def test_cors_preflight_max_age(self):
        self.assertTrue(hasattr(self.conf, "CORS_PREFLIGHT_MAX_AGE"))
        self.assertEqual(type(self.conf.CORS_PREFLIGHT_MAX_AGE), int)

    def test_cors_origin_whitelist(self):
        self.assertTrue(hasattr(self.conf, "CORS_ORIGIN_WHITELIST"))
        self.assertEqual(type(self.conf.CORS_ORIGIN_WHITELIST), tuple)

    def test_cors_allow_headers(self):
        self.assertTrue(hasattr(self.conf, "CORS_ALLOW_HEADERS"))
        self.assertEqual(type(self.conf.CORS_ALLOW_HEADERS), tuple)

    def test_cors_allow_methods(self):
        self.assertTrue(hasattr(self.conf, "CORS_ALLOW_METHODS"))
        self.assertEqual(type(self.conf.CORS_ALLOW_METHODS), tuple)

    def test_cors_expose_headers(self):
        self.assertTrue(hasattr(self.conf, "CORS_EXPOSE_HEADERS"))
        self.assertEqual(type(self.conf.CORS_EXPOSE_HEADERS), tuple)
