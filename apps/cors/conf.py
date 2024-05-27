from django.conf import settings

from apps.cors.defaults import default_headers, default_methods


class Settings:
    """Shadow Django's settings with a little logic"""

    @property
    def CORS_ALLOW_HEADERS(self):
        return getattr(settings, "CORS_ALLOW_HEADERS", default_headers)

    @property
    def CORS_ALLOW_METHODS(self):
        return getattr(settings, "CORS_ALLOW_METHODS", default_methods)

    @property
    def CORS_ALLOW_CREDENTIALS(self):
        return getattr(settings, "CORS_ALLOW_CREDENTIALS", False)

    @property
    def CORS_PREFLIGHT_MAX_AGE(self):
        return getattr(settings, "CORS_PREFLIGHT_MAX_AGE", 86400)

    @property
    def CORS_ORIGIN_ALLOW_ALL(self):
        return getattr(settings, "CORS_ORIGIN_ALLOW_ALL", False)

    @property
    def CORS_ORIGIN_WHITELIST(self):
        return getattr(settings, "CORS_ORIGIN_WHITELIST", ())

    @property
    def CORS_EXPOSE_HEADERS(self):
        return getattr(settings, "CORS_EXPOSE_HEADERS", ())


conf = Settings()
