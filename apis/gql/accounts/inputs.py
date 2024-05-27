import graphene

from apis.gql.accounts.enums import SocialType
from apis.gql.common.fields import Image


class EnableTFAInput(graphene.InputObjectType):
    """Enable TFA authentication input."""

    password = graphene.String(required=True)


class DisableTFAInput(graphene.InputObjectType):
    """Disable TFA authentication input."""

    password = graphene.String(required=True)
    tfa_code = graphene.String(required=True, description="TFA authentication code.")


class SignupTokenInput(graphene.InputObjectType):
    """Signup token input."""

    username = graphene.String(required=True)

    email = graphene.String()
    phone = graphene.String()


class SignupInput(graphene.InputObjectType):
    """Signup input."""

    first_name = graphene.String()
    middle_name = graphene.String()
    last_name = graphene.String()

    username = graphene.String()
    password = graphene.String(required=True)

    email = graphene.String()
    phone = graphene.String()

    birthday = graphene.Date()


class CheckUserInput(graphene.InputObjectType):
    """Check user input."""

    username = graphene.String(required=True)


class CreateUserInput(graphene.InputObjectType):
    """Create user input."""

    username = graphene.String(required=True)
    password = graphene.String(required=True)


class UpdateUserInput(graphene.InputObjectType):
    """Update user input."""

    first_name = graphene.String()
    middle_name = graphene.String()
    last_name = graphene.String()

    email = graphene.String()
    phone = graphene.String()

    birthday = graphene.Date()


class SigninInput(graphene.InputObjectType):
    """Signin input."""

    username = graphene.String(required=True)
    password = graphene.String(required=True)
    tfa_code = graphene.String(description="TFA authentication code.")


class SocialSigninInput(graphene.InputObjectType):
    """Social signin input."""

    social = graphene.NonNull(SocialType)
    token = graphene.String(required=True)
    tfa_code = graphene.String(description="TFA authentication code.")


class ChangePasswordInput(graphene.InputObjectType):
    """Change password input."""

    current = graphene.String(required=True)
    password = graphene.String(required=True)

    expire_keys = graphene.Boolean()


class SendPasswordTokenInput(graphene.InputObjectType):
    """Send password reset token input."""

    username = graphene.String(required=True)


class ResetPasswordInput(graphene.InputObjectType):
    """Reset password input."""

    password = graphene.String(required=True)


class UpdateMeInput(graphene.InputObjectType):
    """Update me input."""

    first_name = graphene.String()
    middle_name = graphene.String()
    last_name = graphene.String()

    birthday = graphene.Date()

    avatar = Image()


class CreateNoteInput(graphene.InputObjectType):
    """Create note input."""

    content = graphene.String(required=True)


class UpdateNoteInput(graphene.InputObjectType):
    """Update note input."""

    content = graphene.String(required=True)


class PersonInput(graphene.InputObjectType):
    """Person input."""

    first_name = graphene.String()
    last_name = graphene.String()

    email = graphene.String(required=True)


class CreateCommentInput(graphene.InputObjectType):
    """Create comment input."""

    content = graphene.String(required=True)
    user = PersonInput(required=True)


class UpdateCommentInput(graphene.InputObjectType):
    """Update comment input."""

    content = graphene.String(required=True)
    user = PersonInput(required=True)
