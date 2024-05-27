import re

from django.http import HttpResponse
from django.utils.cache import patch_vary_headers

from apps.cors.conf import conf

ACCESS_CONTROL_ALLOW_ORIGIN = "Access-Control-Allow-Origin"
ACCESS_CONTROL_EXPOSE_HEADERS = "Access-Control-Expose-Headers"
ACCESS_CONTROL_ALLOW_CREDENTIALS = "Access-Control-Allow-Credentials"
ACCESS_CONTROL_ALLOW_HEADERS = "Access-Control-Allow-Headers"
ACCESS_CONTROL_ALLOW_METHODS = "Access-Control-Allow-Methods"
ACCESS_CONTROL_MAX_AGE = "Access-Control-Max-Age"

ALLOW_HEADERS = ", ".join(conf.CORS_ALLOW_HEADERS)
ALLOW_METHODS = ", ".join(conf.CORS_ALLOW_METHODS)
EXPOSE_HEADERS = ", ".join(conf.CORS_EXPOSE_HEADERS)
ALLOW_CREDENTIALS = conf.CORS_ALLOW_CREDENTIALS
ORIGIN_ALLOW_ALL = conf.CORS_ORIGIN_ALLOW_ALL
ORIGIN_WHITELIST = [re.compile(regex) for regex in conf.CORS_ORIGIN_WHITELIST]
PREFLIGHT_MAX_AGE = conf.CORS_PREFLIGHT_MAX_AGE


class CorsMiddleware:
    """Cors middleware"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.META.get("HTTP_ORIGIN")
        origin_match = self.domain_match(origin)
        enabled = ORIGIN_ALLOW_ALL or origin_match

        if (
            request.method == "OPTIONS"
            and "HTTP_ACCESS_CONTROL_REQUEST_METHOD" in request.META
            and enabled
        ):
            response = HttpResponse()
            response["Content-Length"] = "0"
        else:
            response = self.get_response(request)

        patch_vary_headers(response, ["Origin"])

        if not enabled or not origin:
            return response

        if ALLOW_CREDENTIALS:
            response[ACCESS_CONTROL_ALLOW_CREDENTIALS] = "true"

        if not ORIGIN_ALLOW_ALL and not origin_match:
            return response

        if ORIGIN_ALLOW_ALL and not ALLOW_CREDENTIALS:
            response[ACCESS_CONTROL_ALLOW_ORIGIN] = "*"
        else:
            response[ACCESS_CONTROL_ALLOW_ORIGIN] = origin

        if EXPOSE_HEADERS:
            response[ACCESS_CONTROL_EXPOSE_HEADERS] = EXPOSE_HEADERS

        if request.method == "OPTIONS":
            response[ACCESS_CONTROL_ALLOW_HEADERS] = ALLOW_HEADERS
            response[ACCESS_CONTROL_ALLOW_METHODS] = ALLOW_METHODS
            if PREFLIGHT_MAX_AGE:
                response[ACCESS_CONTROL_MAX_AGE] = PREFLIGHT_MAX_AGE

        return response

    def domain_match(self, origin):
        if not origin:
            return False
        for domain in ORIGIN_WHITELIST:
            if domain.match(origin):
                return True
        return False
