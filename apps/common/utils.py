import string
from base64 import urlsafe_b64encode
from hashlib import sha256
from math import ceil
from secrets import choice
from uuid import uuid4

import jwt
from celery.app import default_app as celery_app
from django.apps import apps
from django.conf import settings
from django.core.cache import cache
from django.utils.module_loading import import_string

default_chars = string.printable[:-6]


class o:
    """o class."""

    pass


def get_client_ip(request):
    """Get client IP address."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_object(model, *args, **kwargs):
    """Get object or none."""
    queryset = getattr(model, "_default_manager", model)
    return queryset.filter(*args, **kwargs).first()


def jwt_encode(payload):
    """JWT encode."""
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


def jwt_decode(token):
    """JWT decode."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])


def unique_id(length=22):
    """Generate an unique id."""
    uid = "".join(
        [
            urlsafe_b64encode(uuid4().bytes).decode().replace("=", "")
            for _ in range(ceil(length / 22))
        ]
    )
    return uid[:length]


def to_object(value):
    """Dict to object."""
    if isinstance(
        value,
        (
            list,
            tuple,
            set,
        ),
    ):
        return [to_object(x) for x in value]
    if not isinstance(value, dict):
        return value

    obj = o()
    for k, v in value.items():
        setattr(obj, k, to_object(v))
    return obj


def random_string(length=20, chars=default_chars):
    """Generate a random string."""
    return "".join([choice(chars) for _ in range(length)])


def send_task(*args, **kwargs):
    """Send task to Celery broker."""
    kwargs["task_id"] = kwargs.get("task_id") or unique_id()
    return celery_app.send_task(*args, **kwargs)


def get_task(app_label, name):
    """Get task from app tasks module."""
    config = apps.get_app_config(app_label)
    return import_string(f"{config.name}.tasks.{name}")


def exec_task(path, *args, **kwargs):
    """Execute Celery task."""
    app_label, name, fn = None, None, "apply_async"
    path = path.split(".")

    if len(path) == 3:
        app_label, name, fn = path
    elif len(path) == 2:
        app_label, name = path

    task = get_task(app_label, name)

    if fn == "call":
        return task(*args, **kwargs)
    if fn == "apply_async":
        kwargs["task_id"] = kwargs.get("task_id") or unique_id()
    return getattr(task, fn)(*args, **kwargs)


def fn_lock(fn, name, id, exc=None, timeout=300, hold=False):
    """Locks function until execution ends."""
    id = sha256(f"{name}:{id}".encode()).hexdigest()
    cache_key = f"fn:lock:{id}"

    if not cache.add(cache_key, 1, timeout):
        message = f'"{name}" locked for {timeout} seconds.'
        if not exc:
            return message
        raise exc(message)

    try:
        result = fn()
    except Exception:
        raise
    finally:
        if not hold:
            cache.delete(cache_key)
    return result


def fn_throttle(fn, name, id, limit, exc=None, timeout=300):
    """Throttle function execution."""
    id = sha256(f"{name}:{id}".encode()).hexdigest()
    cache_key = f"fn:throttle:{id}"

    cache.add(cache_key, 0, timeout)

    try:
        count = cache.incr(cache_key)
    except ValueError:
        count = 0

    if count > limit:
        message = f'"{name}" throttled to {limit} calls every {timeout} seconds.'
        if not exc:
            return message
        raise exc(message)

    try:
        result = fn()
    except Exception:
        raise
    return result
