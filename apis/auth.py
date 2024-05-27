from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.common.utils import get_object, jwt_decode, to_object

User = get_user_model()


def auth_user(cls, ctx, exc=True):
    """Auth user."""
    try:
        ctx.user = cls.authenticate(ctx)
    except AuthError:
        if exc:
            raise


def auth_test(cls):
    """Auth fn test."""

    def fn_test(ctx):
        auth_user(cls, ctx)
        return ctx.user.is_authenticated

    return fn_test


def get_authorization_header(request):
    """Return request's 'Authorization:' header, as a bytestring."""
    auth = request.META.get("HTTP_AUTHORIZATION", b"")
    if isinstance(auth, str):
        auth = auth.encode()
    return auth


class AuthError(Exception):
    """Auth error."""

    pass


class BaseAuth:
    """All auth classes should extend BaseAuth."""

    @classmethod
    def authenticate(cls, request):
        """Authenticate the request and return an user instance."""
        raise NotImplementedError


class TokenAuth(BaseAuth):
    """Token auth."""

    keyword = "Bearer"
    typ = settings.AUTH_TOKEN_TYPE
    model = User

    @classmethod
    def authenticate(cls, request):
        auth = get_authorization_header(request).split()

        if not auth or auth[0] != cls.keyword.encode():
            raise AuthError(_("The token was not provided."))
        if len(auth) != 2:
            raise AuthError(_("The token should not contain spaces."))

        try:
            token = auth[1].decode()
        except UnicodeError:
            raise AuthError(_("The token should not contain invalid characters."))

        payload = cls.validate_key(request, token)
        user = cls.validate_user(request, payload)

        return user

    @classmethod
    def validate_key(cls, request, key):
        try:
            payload = jwt_decode(key)
        except Exception:
            raise AuthError(_("The token provided is wrong."))

        if payload.get("typ") != cls.typ:
            raise AuthError(_('The token type should be "%s".') % cls.typ)

        return payload

    @classmethod
    def validate_user(cls, request, payload):
        if hasattr(request, "_user_check"):
            user = request.user
        else:
            request._user_check = True
            user = get_object(cls.model, pk=payload.get("sub"))

        if not user:
            raise AuthError(_("The user does not exist."))
        if not user.is_active:
            raise AuthError(_("The user is inactive."))
        if payload.get("rnd") != user.rnd:
            raise AuthError(_("The token has been revoked."))

        return user


class RefreshTokenAuth(TokenAuth):
    """Refresh token auth."""

    typ = settings.AUTH_REFRESH_TOKEN_TYPE


class PasswdTokenAuth(TokenAuth):
    """Reset password token auth."""

    typ = settings.PASSWD_TOKEN_TYPE


class SignupTokenAuth(TokenAuth):
    """Signup token auth."""

    typ = settings.SIGNUP_TOKEN_TYPE

    @classmethod
    def validate_user(cls, request, payload):
        user = to_object(
            {
                "pk": None,
                "username": payload.get("sub"),
                "email": payload.get("eml"),
                "phone": payload.get("phe"),
                "is_active": True,
                "is_authenticated": True,
            }
        )
        return user
