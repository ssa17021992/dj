from hashlib import md5

from django.contrib.auth import get_user_model

from apps.accounts.auth.backends.base import BaseAuthBackend
from apps.common.utils import get_object

User = get_user_model()


class AuthBackend(BaseAuthBackend):
    """Dummy auth backend."""

    def get_user(self, user_data):
        username = "dummy.%(id)s" % user_data
        user = get_object(User, username=username)

        if not user:
            user = User(username=username, email=user_data["email"])
            user.set_unusable_password()
            user.save()

        return user

    def signin(self, token):
        return self.get_user(
            {
                "id": md5(token.encode()).hexdigest(),
                "email": "dummy@mail.com",
            }
        )
