from django.conf import settings
from graphene import Enum

if settings.USE_DUMMY:

    class SocialType(Enum):
        """Social type enum."""

        DUMMY = "dummy"
        FACEBOOK = "facebook"
        GOOGLE = "google"

else:

    class SocialType(Enum):
        """Social type enum."""

        FACEBOOK = "facebook"
        GOOGLE = "google"
