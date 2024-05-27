from rest_framework import pagination


class PageNumberPagination(pagination.PageNumberPagination):
    """Page number pagination."""

    page_size = 10
    max_page_size = 50
    page_size_query_param = "limit"
    page_query_param = "page"


class LimitOffsetPagination(pagination.LimitOffsetPagination):
    """Limit offset pagination."""

    default_limit = 10
    max_limit = 50
    limit_query_param = "limit"
    offset_query_param = "offset"


class CursorPagination(pagination.CursorPagination):
    """Cursor pagination."""

    page_size = 10
    max_page_size = 50
    page_size_query_param = "limit"
    cursor_query_params = "cursor"
    ordering = "id"
