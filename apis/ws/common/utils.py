import json

from channels.db import database_sync_to_async as db_async  # noqa


def ws_response(action=None, data=None, error=None):
    """Get JSON response data."""
    data = {
        "action": action,
        "data": data,
        "error": error,
    }
    return json.dumps(
        data,
        separators=(
            ",",
            ":",
        ),
        ensure_ascii=False,
    )


def ws_data(action=None, data=None):
    """Get JSON data."""
    return ws_response(action, data=data)


def ws_error(action=None, field=None, message=""):
    """Get JSON error."""
    error = {
        "field": field,
        "message": str(message),
    }
    return ws_response(action, error=error)
