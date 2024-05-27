from functools import wraps

from django.contrib.auth.models import AnonymousUser

from apps.common.utils import fn_lock, fn_throttle


def session_user_exempt(view_func):
    """Cleans the user assigned by the session middleware."""

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        user = AnonymousUser()
        request.user = user
        request._cached_user = user
        return view_func(request, *args, **kwargs)

    return wrapped_view


def task_lock(name="Lock", attr="id", timeout=600, hold=False):
    """Locks task until execution ends."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if hasattr(attr, "__call__"):
                id = attr(*args, **kwargs)
            else:
                id = kwargs.get(attr)
            return fn_lock(lambda: fn(*args, **kwargs), name, id, None, timeout, hold)

        return wrapper

    return decorator


def task_throttle(name="Throttle", attr="id", limit=1, timeout=600):
    """Throttle task execution."""

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            if hasattr(attr, "__call__"):
                id = attr(*args, **kwargs)
            else:
                id = kwargs.get(attr)
            return fn_throttle(
                lambda: fn(*args, **kwargs), name, id, limit, None, timeout
            )

        return wrapper

    return decorator
