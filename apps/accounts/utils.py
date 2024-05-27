from time import time

from django.conf import settings

from apps.common.utils import jwt_encode


def auth_token(user):
    """Generate authentication token"""
    now = int(time())
    payload = {
        "sub": user.pk,
        "typ": settings.AUTH_TOKEN_TYPE,
        "rnd": user.rnd,
        "iat": now,
        "exp": now + settings.AUTH_TOKEN_AGE,
    }
    return jwt_encode(payload)


def auth_refresh_token(user):
    """Generate authentication refresh token"""
    now = int(time())
    payload = {
        "sub": user.pk,
        "typ": settings.AUTH_REFRESH_TOKEN_TYPE,
        "rnd": user.rnd,
        "iat": now,
        "exp": now + settings.AUTH_REFRESH_TOKEN_AGE,
    }
    return jwt_encode(payload)


def passwd_token(user):
    """Generate password reset token"""
    now = int(time())
    payload = {
        "sub": user.pk,
        "typ": settings.PASSWD_TOKEN_TYPE,
        "rnd": user.rnd,
        "iat": now,
        "exp": now + settings.PASSWD_TOKEN_AGE,
    }
    return jwt_encode(payload)


def signup_token(user):
    """Generate signup token"""
    now = int(time())
    payload = {
        "sub": user.username,
        "typ": settings.SIGNUP_TOKEN_TYPE,
        "eml": user.email,
        "phe": user.phone,
        "iat": now,
        "exp": now + settings.SIGNUP_TOKEN_AGE,
    }
    return jwt_encode(payload)
