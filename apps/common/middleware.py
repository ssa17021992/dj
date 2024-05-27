import logging

try:
    import zoneinfo
except ImportError:
    import pytz

    zoneinfo = pytz
    zoneinfo.ZoneInfo = pytz.timezone
    zoneinfo.ZoneInfoNotFoundError = pytz.exceptions.UnknownTimeZoneError

from django.conf import settings
from django.db import connection
from django.utils import timezone, translation

sql_logger = logging.getLogger("sql.console")


class RequestIDMiddleware:
    """Request ID middleware."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request_id = request.META.get("HTTP_X_REQUEST_ID", "")
        response = self.get_response(request)
        response.headers["X-Request-ID"] = request_id
        return response


class LocaleMiddleware:
    """Locale middleware"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        language_code = request.GET.get("lc")

        if language_code:
            translation.activate(language_code)

        response = self.get_response(request)
        translation.deactivate()
        return response


class TimeZoneMiddleware:
    """Time zone middleware"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        zone_info = self.get_zone_info(
            request.GET.get("tz") or request.META.get("HTTP_X_TIME_ZONE")
        )

        if zone_info:
            timezone.activate(zone_info)

        response = self.get_response(request)
        timezone.deactivate()
        return response

    def get_zone_info(self, name):
        if not name:
            return None
        try:
            zone = zoneinfo.ZoneInfo(name)
        except zoneinfo.ZoneInfoNotFoundError:
            return None
        return zone


class SQLDebugMiddleware:
    """SQL debug middleware"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if not settings.DEBUG or not connection.queries:
            return response

        time = 0.0
        count = 0
        for query in connection.queries:
            time += float(query["time"])
            count += 1
            query["count"] = count
            sql_logger.debug("%s", "(%(time)s) %(count)d %(sql)s" % query)

        sql_logger.debug("%s", "(%.3f) %d SQL queries" % (time, count))
        return response
