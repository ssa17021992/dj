from functools import wraps

from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied

from apis import auth
from apis.auth import auth_test, auth_user
from apis.pi.decorators import ctx


def pass_test(fn_test, field="perm", message=_("Permission denied.")):
    """Pass test."""

    def decorator(fn):
        @wraps(fn)
        @ctx
        def wrapper(ctx, *args, **kwargs):
            try:
                if not fn_test(ctx):
                    raise PermissionDenied({field: message})
            except auth.AuthError as e:
                raise AuthenticationFailed({field: str(e)})
            return fn(*args, **kwargs)

        return wrapper

    return decorator


def has_perm(perm):
    """Has permission."""
    message = _('"%(perm)s" permission is required to perform this action.') % {
        "perm": perm,
    }

    def decorator(fn):
        @wraps(fn)
        @pass_test(lambda ctx: ctx.user.has_perm(perm), message=message)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)

        return wrapper

    return decorator


auth_required = pass_test(
    auth_test(auth.TokenAuth), field="auth", message=_("Authentication failed.")
)

refresh_token_required = pass_test(
    auth_test(auth.RefreshTokenAuth), field="auth", message=_("Authentication failed.")
)

signup_token_required = pass_test(
    auth_test(auth.SignupTokenAuth), field="auth", message=_("Authentication failed.")
)

passwd_token_required = pass_test(
    auth_test(auth.PasswdTokenAuth), field="auth", message=_("Authentication failed.")
)


def auth_required_no_exc(fn):
    """Auth required no exc."""

    @wraps(fn)
    @ctx
    def wrapper(ctx, *args, **kwargs):
        auth_user(auth.TokenAuth, ctx, exc=False)
        return fn(*args, **kwargs)

    return wrapper


def staff_required(fn):
    """Staff required."""
    message = _("Staff permission is required to perform this action.")

    @wraps(fn)
    @auth_required
    @pass_test(lambda ctx: ctx.user.is_staff, message=message)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper


def superuser_required(fn):
    """Superuser required."""
    message = _("Superuser permission is required to perform this action.")

    @wraps(fn)
    @auth_required
    @pass_test(lambda ctx: ctx.user.is_superuser, message=message)
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs)

    return wrapper
