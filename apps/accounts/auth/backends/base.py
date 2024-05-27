"""Base auth backend class."""


class BaseAuthBackend:
    """Base auth backend."""

    def get_user(self, user_data):
        pass

    def signin(self, token):
        pass
