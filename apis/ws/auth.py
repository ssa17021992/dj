from functools import wraps
from io import BytesIO
from urllib.parse import parse_qs

from django.contrib.auth.models import AnonymousUser
from django.core.handlers.wsgi import WSGIRequest
from django.utils.translation import gettext_lazy as _

from apis.auth import TokenAuth, auth_user
from apis.ws.common.utils import db_async, ws_error

UNAUTHORIZED = 4401
PERMISSION_DENIED = 4403


def _ctx_request(fn):
    """Context WSGIRequest."""

    @wraps(fn)
    async def wrapper(ws, *args, **kwargs):
        if not hasattr(ws, "ctx"):
            key = parse_qs(ws.scope["query_string"]).get(b"auth")
            ctx = WSGIRequest(
                {
                    "REQUEST_METHOD": "GET",
                    "PATH_INFO": "/ws",
                    "wsgi.input": BytesIO(),
                }
            )
            if key:
                ctx.META["HTTP_AUTHORIZATION"] = b"%s %s" % (
                    TokenAuth.keyword.encode(),
                    key[0],
                )
            ctx.user = AnonymousUser()
            ws.ctx = ctx
        return await fn(ws, *args, **kwargs)

    return wrapper


def ctx(fn):
    """WebSocket context."""

    @wraps(fn)
    @_ctx_request
    async def wrapper(ws, *args, **kwargs):
        await db_async(auth_user)(TokenAuth, ws.ctx, exc=False)
        return await fn(ws, *args, **kwargs)

    return wrapper


def pass_test(fn_test, field="perm", message=_("Permission denied."), close_code=None):
    """Pass test."""

    def decorator(fn):
        @wraps(fn)
        @ctx
        async def wrapper(ws, *args, **kwargs):
            if not await db_async(fn_test)(ws):
                if close_code is not None:
                    return await ws.close(code=close_code)
                return await ws.send(text_data=ws_error(field=field, message=message))
            return await fn(ws, *args, **kwargs)

        return wrapper

    return decorator


def has_perm(perm):
    """Has permission."""
    message = _('"%(perm)s" permission is required to perform this action.') % {
        "perm": perm,
    }

    def decorator(fn):
        @wraps(fn)
        @pass_test(lambda ws: ws.ctx.user.has_perm(perm), message=message)
        async def wrapper(*args, **kwargs):
            return await fn(*args, **kwargs)

        return wrapper

    return decorator


auth_required = pass_test(
    lambda ws: ws.ctx.user.is_authenticated, close_code=UNAUTHORIZED
)

staff_required = pass_test(
    lambda ws: ws.ctx.user.is_staff, close_code=PERMISSION_DENIED
)

superuser_required = pass_test(
    lambda ws: ws.ctx.user.is_superuser, close_code=PERMISSION_DENIED
)
