from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from apps.accounts.auth.backends.base import BaseAuthBackend
from apps.accounts.auth.backends.facebook import facebook
from apps.accounts.auth.exceptions import AuthError
from apps.common.utils import get_object

User = get_user_model()


class AuthBackend(BaseAuthBackend):
    """Facebook auth backend."""

    def get_user(self, user_data):
        username = "fb.%(id)s" % user_data
        user = get_object(User, username=username)

        if not user:
            user = User(
                first_name=user_data.get("first_name") or "",
                middle_name=user_data.get("middle_name") or "",
                last_name=user_data.get("last_name") or "",
                username=username,
                email=user_data["email"] or "",
            )
            user.set_unusable_password()
            user.save()

        return user

    def signin(self, token):
        required_fields = (
            "id",
            "email",
        )

        try:
            me = facebook.FacebookClient(token).me()
        except facebook.FacebookError as e:
            raise AuthError("facebook", e.message)

        if me.get("error"):
            raise AuthError("facebook", me["error"]["message"])

        facebook_fields = me.keys()

        if set(required_fields) & set(facebook_fields) != set(required_fields):
            message = _(
                "Invalid %(social)s fields "
                '"%(facebook_fields)s", must be "%(required_fields)s".'
            )
            raise AuthError(
                "token",
                message
                % {
                    "social": "facebook",
                    "facebook_fields": ", ".join(facebook_fields),
                    "required_fields": ", ".join(required_fields),
                },
            )

        return self.get_user(me)
