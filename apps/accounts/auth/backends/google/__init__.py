from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.accounts.auth.backends.base import BaseAuthBackend
from apps.accounts.auth.backends.google import google
from apps.accounts.auth.exceptions import AuthError
from apps.common.utils import get_object

User = get_user_model()


class AuthBackend(BaseAuthBackend):
    """Google auth backend."""

    def get_user(self, user_data):
        username = "go.%(sub)s" % user_data
        user = get_object(User, username=username)

        if not user:
            user = User(
                first_name=user_data.get("given_name") or "",
                middle_name=user_data.get("family_name") or "",
                username=username,
                email=user_data["email"] or "",
            )
            user.set_unusable_password()
            user.save()

        return user

    def signin(self, token):
        required_fields = (
            "sub",
            "email",
        )

        try:
            me = google.GoogleClient(token).me()
        except google.GoogleError as e:
            raise AuthError("google", e.message)

        if me.get("error"):
            raise AuthError("google", me["error"]["message"])

        google_fields = me.keys()

        if set(required_fields) & set(google_fields) != set(required_fields):
            message = _(
                "Invalid %(social)s fields "
                '"%(google_fields)s", must be "%(required_fields)s".'
            )
            raise AuthError(
                "token",
                message
                % {
                    "social": "google",
                    "google_fields": ", ".join(google_fields),
                    "required_fields": ", ".join(required_fields),
                },
            )

        return self.get_user(me)
