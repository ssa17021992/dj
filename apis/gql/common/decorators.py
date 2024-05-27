from functools import wraps

from django.core.exceptions import ValidationError
from graphene import ResolveInfo

from apps.common.utils import fn_lock, fn_throttle, get_client_ip


def ctx(fn):
    """Context."""

    @wraps(fn)
    def wrapper(*args, **kwargs):
        arg = next(arg for arg in args if isinstance(arg, ResolveInfo))
        return fn(arg.context, *args, **kwargs)

    return wrapper


def gql_lock(name="Lock", attr="client_ip", timeout=300, hold=False):
    """Locks until execution ends."""
    exc = lambda message: ValidationError({"lock": message})  # noqa

    def decorator(fn):
        @wraps(fn)
        @ctx
        def wrapper(ctx, *args, **kwargs):
            if attr == "client_ip":
                id = get_client_ip(ctx)
            elif hasattr(attr, "__call__"):
                id = attr(ctx, *args, **kwargs)
            else:
                id = kwargs.get(attr)
            return fn_lock(lambda: fn(*args, **kwargs), name, id, exc, timeout, hold)

        return wrapper

    return decorator


def gql_throttle(name="Throttle", attr="client_ip", limit=1, timeout=300):
    """Throttle execution."""
    exc = lambda message: ValidationError({"throttle": message})  # noqa

    def decorator(fn):
        @wraps(fn)
        @ctx
        def wrapper(ctx, *args, **kwargs):
            if attr == "client_ip":
                id = get_client_ip(ctx)
            elif hasattr(attr, "__call__"):
                id = attr(ctx, *args, **kwargs)
            else:
                id = kwargs.get(attr)
            return fn_throttle(
                lambda: fn(*args, **kwargs), name, id, limit, exc, timeout
            )

        return wrapper

    return decorator
