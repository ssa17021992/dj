"""Auth backend error class."""


class AuthError(Exception):
    """Auth error."""

    def __init__(self, field, message):
        self.field = field
        self.message = message
