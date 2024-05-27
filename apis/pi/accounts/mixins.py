class SigninMixin:
    """Signin mixin"""

    def get_response_data(self, serializer):
        user = serializer.instance
        return {
            "token": user.get_token(),
            "refresh_token": user.get_refresh_token(),
            "user": super().get_response_data(serializer),
        }
