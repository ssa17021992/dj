import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from apis.gql.accounts import inputs, types
from apis.gql.auth import (
    auth_required,
    has_perm,
    passwd_token_required,
    refresh_token_required,
    signup_token_required,
    staff_required,
)
from apis.gql.common.decorators import gql_lock, gql_throttle
from apps.accounts import models
from apps.accounts.auth.exceptions import AuthError
from apps.accounts.auth.utils import get_auth_backend
from apps.accounts.utils import signup_token
from apps.common.utils import exec_task, get_object, to_object, unique_id
from apps.gql import mutations

User = get_user_model()


class EnableTFA(mutations.Mutation):
    """Enable TFA authentication."""

    user = graphene.Field(types.User)
    qr_code = graphene.String(description="QR code TOTP URI.")

    class Arguments:
        input = inputs.EnableTFAInput(
            required=True, description="Enable TFA authentication input."
        )

    class Meta:
        description = "Enable TFA authentication."
        field_name = "tfa_secret"
        field_type = graphene.String

    @classmethod
    def clean_input(cls, info, input):
        if not input["password"]:
            raise ValidationError(
                {
                    "password": _("This field is required."),
                }
            )
        return input

    @classmethod
    def success_response(cls, info, instance):
        return cls(
            **{
                cls._meta.field_name: instance,
                "user": info.context.user,
                "qr_code": info.context.user.totp_qr_code,
            }
        )

    @classmethod
    @gql_lock(name="EnableTFA")
    @auth_required
    def perform_mutation(cls, root, info, input, **kwargs):
        user = info.context.user
        cleaned_input = cls.clean_input(info, input)

        if user.tfa_active:
            raise ValidationError(
                {
                    "tfa_secret": _("The TFA authentication is already enabled."),
                }
            )
        if not user.check_password(cleaned_input["password"]):
            raise ValidationError(
                {
                    "password": _("Wrong password."),
                }
            )
        return user.enable_tfa()


class DisableTFA(mutations.Mutation):
    """Disable TFA authentication."""

    user = graphene.Field(types.User)

    class Arguments:
        input = inputs.DisableTFAInput(
            required=True, description="Disable TFA authentication input."
        )

    class Meta:
        description = "Disable TFA authentication."
        field_name = "tfa_secret"
        field_type = graphene.String

    @classmethod
    def clean_input(cls, info, input):
        if not input["password"]:
            raise ValidationError(
                {
                    "password": _("This field is required."),
                }
            )
        if not input["tfa_code"]:
            raise ValidationError(
                {
                    "tfa_code": _("This field is required."),
                }
            )
        return input

    @classmethod
    def success_response(cls, info, instance):
        return cls(
            **{
                cls._meta.field_name: instance,
                "user": info.context.user,
            }
        )

    @classmethod
    @gql_lock(name="DisableTFA")
    @auth_required
    def perform_mutation(cls, root, info, input, **kwargs):
        user = info.context.user
        cleaned_input = cls.clean_input(info, input)

        if not user.tfa_active:
            raise ValidationError(
                {
                    "tfa_secret": _("The TFA authentication is not enabled."),
                }
            )
        if not user.check_password(cleaned_input["password"]):
            raise ValidationError(
                {
                    "password": _("Wrong password."),
                }
            )
        if not user.check_tfa_code(cleaned_input["tfa_code"]):
            raise ValidationError(
                {
                    "tfa_code": _("Wrong TFA authentication code."),
                }
            )
        return user.disable_tfa()


class Signin(mutations.Mutation):
    """Signin."""

    user = graphene.Field(types.User)
    refresh_token = graphene.String()

    class Arguments:
        input = inputs.SigninInput(required=True, description="Signin input.")

    class Meta:
        description = "Signin."
        field_name = "token"
        field_type = graphene.String

    @classmethod
    def clean_input(cls, info, input):
        if not input["username"]:
            raise ValidationError(
                {
                    "username": _("This field is required."),
                }
            )
        if not input["password"]:
            raise ValidationError(
                {
                    "password": _("This field is required."),
                }
            )
        return input

    @classmethod
    def clean_tfa_input(cls, info, input):
        if not input.get("tfa_code"):
            raise ValidationError(
                {
                    "tfa_code": _("This field is required."),
                }
            )
        return input

    @classmethod
    def success_response(cls, info, instance):
        return cls(
            **{
                cls._meta.field_name: instance,
                "user": info.context.user,
                "refresh_token": info.context.user.get_refresh_token(),
            }
        )

    @classmethod
    @gql_lock(name="Signin")
    @gql_throttle(name="Signin", limit=3, timeout=600)
    def perform_mutation(cls, root, info, input, **kwargs):
        cleaned_input = cls.clean_input(info, input)
        user = get_object(User, username=cleaned_input["username"])

        if not user:
            raise ValidationError(
                {
                    "username": _("User does not exist."),
                }
            )
        if not user.is_active:
            raise ValidationError(
                {
                    "username": _("User inactive."),
                }
            )
        if not user.check_password(cleaned_input["password"]):
            raise ValidationError(
                {
                    "password": _("Wrong password."),
                }
            )
        if user.tfa_active:
            cleaned_input = cls.clean_tfa_input(info, input)
            if not user.check_tfa_code(cleaned_input["tfa_code"]):
                raise ValidationError(
                    {
                        "tfa_code": _("Wrong TFA authentication code."),
                    }
                )

        user.update_last_login()
        setattr(info.context, "user", user)
        return user.get_token()


class SocialSignin(mutations.Mutation):
    """Social signin."""

    user = graphene.Field(types.User)
    refresh_token = graphene.String()

    class Arguments:
        input = inputs.SocialSigninInput(
            required=True, description="Social signin input."
        )

    class Meta:
        description = "Social signin."
        field_name = "token"
        field_type = graphene.String

    @classmethod
    def clean_input(cls, info, input):
        if not input["token"]:
            raise ValidationError(
                {
                    "token": _("This field is required."),
                }
            )
        return input

    @classmethod
    def clean_tfa_input(cls, info, input):
        if not input.get("tfa_code"):
            raise ValidationError(
                {
                    "tfa_code": _("This field is required."),
                }
            )
        return input

    @classmethod
    def success_response(cls, info, instance):
        return cls(
            **{
                cls._meta.field_name: instance,
                "user": info.context.user,
                "refresh_token": info.context.user.get_refresh_token(),
            }
        )

    @classmethod
    @gql_lock(name="SocialSignin")
    @gql_throttle(name="SocialSignin", limit=3, timeout=600)
    def perform_mutation(cls, root, info, input, **kwargs):
        cleaned_input = cls.clean_input(info, input)
        auth_backend = get_auth_backend(cleaned_input["social"].value)

        try:
            user = auth_backend.signin(cleaned_input["token"])
        except AuthError as e:
            raise ValidationError({e.field: e.message})

        if not user.is_active:
            raise ValidationError(
                {
                    "username": _("User inactive."),
                }
            )
        if user.tfa_active:
            cleaned_input = cls.clean_tfa_input(info, input)
            if not user.check_tfa_code(cleaned_input["tfa_code"]):
                raise ValidationError(
                    {
                        "tfa_code": _("Wrong TFA authentication code."),
                    }
                )

        user.update_last_login()
        setattr(info.context, "user", user)
        return user.get_token()


class RefreshToken(mutations.Mutation):
    """Refresh token."""

    user = graphene.Field(types.User)

    class Meta:
        description = "Refresh token."
        field_name = "token"
        field_type = graphene.String

    @classmethod
    def success_response(cls, info, instance):
        return cls(
            **{
                cls._meta.field_name: instance,
                "user": info.context.user,
            }
        )

    @classmethod
    @gql_lock(name="RefreshToken")
    @refresh_token_required
    def perform_mutation(cls, root, info, **kwargs):
        return info.context.user.get_token()


class CheckUser(mutations.Mutation):
    """Check user."""

    class Arguments:
        input = inputs.CheckUserInput(required=True, description="Check user input.")

    class Meta:
        description = "Check if an username is available."
        field_name = "available"
        field_type = graphene.Boolean

    @classmethod
    def clean_input(cls, info, input):
        if not input["username"]:
            raise ValidationError(
                {
                    "username": _("This field is required."),
                }
            )
        return input

    @classmethod
    @gql_lock(name="CheckUser")
    def perform_mutation(cls, root, info, input, **kwargs):
        cleaned_input = cls.clean_input(info, input)
        return not User.objects.filter(username=cleaned_input["username"]).exists()


class SendSignupToken(mutations.Mutation):
    """Send signup token."""

    class Arguments:
        input = inputs.SignupTokenInput(
            required=True, description="Signup token input."
        )

    class Meta:
        description = "Send signup token."
        field_name = "success"
        field_type = graphene.Boolean

    @classmethod
    def clean_input(cls, info, input):
        if not input["email"]:
            raise ValidationError(
                {
                    "email": _("This field is required."),
                }
            )
        return input

    @classmethod
    @gql_lock(name="SendSignupToken")
    @gql_throttle(name="SendSignupToken", limit=1)
    def perform_mutation(cls, root, info, input, **kwargs):
        input = {
            "email": "",
            "phone": "",
            **input,
        }
        cleaned_input = cls.clean_input(info, input)
        user = to_object(cleaned_input)
        exec_task(
            "accounts.send_signup_mail",
            args=(
                signup_token(user),
                user.email,
            ),
        )
        return True


class CheckSignupToken(mutations.Mutation):
    """Check signup token."""

    class Meta:
        description = "Check signup token."
        field_name = "success"
        field_type = graphene.Boolean

    @classmethod
    @signup_token_required
    def perform_mutation(cls, root, info, **kwargs):
        return True


class Signup(mutations.ModelMutation):
    """Signup."""

    class Arguments:
        input = inputs.SignupInput(required=True, description="Signup input.")

    class Meta:
        description = "Signup."
        model = User
        field_name = "user"
        field_type = types.User

    @classmethod
    def save(cls, info, instance, cleaned_input):
        instance.set_password(cleaned_input["password"])
        instance.save()

    @classmethod
    @gql_lock(name="Signup")
    @signup_token_required
    def perform_mutation(cls, root, info, **kwargs):
        user = info.context.user
        kwargs["input"].update(
            {
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
            }
        )
        return super().perform_mutation(root, info, **kwargs)


class ChangePassword(mutations.Mutation):
    """Change the user password."""

    class Arguments:
        input = inputs.ChangePasswordInput(
            required=True, description="Change password input."
        )

    class Meta:
        description = "Change the user password."
        field_name = "success"
        field_type = graphene.Boolean

    @classmethod
    def clean_input(cls, info, input, instance):
        if not input["current"]:
            raise ValidationError(
                {
                    "current": _("This field is required."),
                }
            )
        if not input["password"]:
            raise ValidationError(
                {
                    "password": _("This field is required."),
                }
            )
        if not instance.check_password(input["current"]):
            raise ValidationError(
                {
                    "current": _("Wrong password."),
                }
            )
        if input["current"] == input["password"]:
            raise ValidationError(
                {
                    "password": _("Current and new password cannot be same."),
                }
            )
        return input

    @classmethod
    def save(cls, info, instance, cleaned_input):
        instance.set_password(
            cleaned_input["password"], expire_keys=cleaned_input["expire_keys"]
        )
        instance.save(
            update_fields=[
                "password",
                "renewed",
            ]
        )

    @classmethod
    @gql_lock(name="ChangePassword")
    @auth_required
    def perform_mutation(cls, root, info, input, **kwargs):
        user = info.context.user
        input = {
            "expire_keys": True,
            **input,
        }
        cleaned_input = cls.clean_input(info, input, user)
        cls.save(info, user, cleaned_input)
        return True


class SendPasswordToken(mutations.Mutation):
    """Send token to reset user password."""

    class Arguments:
        input = inputs.SendPasswordTokenInput(
            required=True, description="Send password reset token input."
        )

    class Meta:
        description = "Send token to reset user password."
        field_name = "success"
        field_type = graphene.Boolean

    @classmethod
    def clean_input(cls, info, input):
        if not input["username"]:
            raise ValidationError(
                {
                    "username": _("This field is required."),
                }
            )
        return input

    @classmethod
    @gql_lock(name="SendPasswordToken")
    @gql_throttle(name="SendPasswordToken", limit=1)
    def perform_mutation(cls, root, info, input, **kwargs):
        cleaned_input = cls.clean_input(info, input)
        user = get_object(User, username=cleaned_input["username"])

        if not user:
            raise ValidationError(
                {
                    "username": _("User does not exist."),
                }
            )

        exec_task(
            "accounts.send_passwd_reset_mail",
            args=(
                user.get_passwd_token(),
                user.username,
                user.email,
            ),
        )
        return True


class CheckPasswordToken(mutations.Mutation):
    """Check password reset token."""

    class Meta:
        description = "Check password reset token."
        field_name = "success"
        field_type = graphene.Boolean

    @classmethod
    @passwd_token_required
    def perform_mutation(cls, root, info, **kwargs):
        return True


class ResetPassword(mutations.Mutation):
    """Reset password."""

    class Arguments:
        input = inputs.ResetPasswordInput(
            required=True, description="Reset password input."
        )

    class Meta:
        description = "Reset password."
        field_name = "success"
        field_type = graphene.Boolean

    @classmethod
    def clean_input(cls, info, input):
        if not input["password"]:
            raise ValidationError(
                {
                    "password": _("This field is required."),
                }
            )
        return input

    @classmethod
    def save(cls, info, instance, cleaned_input):
        instance.set_password(cleaned_input["password"], expire_keys=True)
        instance.save(
            update_fields=[
                "password",
                "renewed",
            ]
        )

    @classmethod
    @gql_lock(name="ResetPassword")
    @passwd_token_required
    def perform_mutation(cls, root, info, input, **kwargs):
        user = info.context.user
        cleaned_input = cls.clean_input(info, input)
        cls.save(info, user, cleaned_input)
        return True


class UpdateMe(mutations.ModelMutation):
    """Update me information."""

    class Arguments:
        input = inputs.UpdateMeInput(required=True, description="Update me input.")

    class Meta:
        description = "Update me information."
        model = User
        exclude = ("username",)
        field_name = "me"
        field_type = types.User

    @classmethod
    def get_instance(cls, info, **kwargs):
        return info.context.user

    @classmethod
    @gql_lock(name="UpdateMe")
    @auth_required
    def perform_mutation(cls, root, info, **kwargs):
        return super().perform_mutation(root, info, **kwargs)


class CreateNote(mutations.ModelMutation):
    """Create note."""

    class Arguments:
        input = inputs.CreateNoteInput(required=True, description="Create note input.")

    class Meta:
        description = "Create note."
        model = models.Note
        exclude = (
            "id",
            "user",
        )
        field_name = "note"
        field_type = types.Note

    @classmethod
    def save(cls, info, instance, cleaned_input):
        instance.user = info.context.user
        instance.save()

    @classmethod
    @gql_lock(name="CreateNote")
    @auth_required
    def perform_mutation(cls, root, info, **kwargs):
        return super().perform_mutation(root, info, **kwargs)


class UpdateNote(mutations.ModelMutation):
    """Update note."""

    class Arguments:
        id = graphene.ID(required=True, description="Note ID.")
        input = inputs.UpdateNoteInput(required=True, description="Update note input.")

    class Meta:
        description = "Update note."
        model = models.Note
        exclude = ("user",)
        field_name = "note"
        field_type = types.Note

    @classmethod
    def get_instance(cls, info, **kwargs):
        instance = super().get_instance(info, **kwargs)

        if instance.user_id != info.context.user.pk:
            raise ValidationError(
                {
                    "perm": _("Permission denied."),
                }
            )
        return instance

    @classmethod
    @gql_lock(name="UpdateNote", attr="id")
    @auth_required
    def perform_mutation(cls, root, info, **kwargs):
        return super().perform_mutation(root, info, **kwargs)


class DeleteNote(mutations.ModelDeleteMutation):
    """Delete note."""

    class Arguments:
        id = graphene.ID(required=True, description="Note ID.")

    class Meta:
        description = "Delete note."
        model = models.Note
        field_name = "note"
        field_type = types.Note

    @classmethod
    def get_instance(cls, info, **kwargs):
        instance = super().get_instance(info, **kwargs)

        if instance.user_id != info.context.user.pk:
            raise ValidationError(
                {
                    "perm": _("Permission denied."),
                }
            )
        return instance

    @classmethod
    @gql_lock(name="DeleteNote", attr="id")
    @auth_required
    def perform_mutation(cls, root, info, **kwargs):
        return super().perform_mutation(root, info, **kwargs)


class CreateUser(mutations.ModelMutation):
    """Create user."""

    class Arguments:
        input = inputs.CreateUserInput(required=True, description="Create user input.")

    class Meta:
        description = "Create an user."
        model = User
        exclude = ("id",)
        field_name = "user"
        field_type = types.User

    @classmethod
    def save(cls, info, instance, cleaned_input):
        instance.set_password(cleaned_input["password"])
        instance.save()

    @classmethod
    @gql_lock(name="CreateUser")
    @staff_required
    @has_perm("accounts.add_user")
    def perform_mutation(cls, root, info, **kwargs):
        return super().perform_mutation(root, info, **kwargs)


class UpdateUser(mutations.ModelMutation):
    """Update user."""

    class Arguments:
        id = graphene.ID(required=True, description="User ID.")
        input = inputs.UpdateUserInput(required=True, description="Update user input.")

    class Meta:
        description = "Update an user."
        model = User
        exclude = ("username",)
        field_name = "user"
        field_type = types.User

    @classmethod
    @gql_lock(name="UpdateUser", attr="id")
    @staff_required
    @has_perm("accounts.change_user")
    def perform_mutation(cls, root, info, **kwargs):
        return super().perform_mutation(root, info, **kwargs)


class DeleteUser(mutations.ModelDeleteMutation):
    """Delete user."""

    class Arguments:
        id = graphene.ID(required=True, description="User ID.")

    class Meta:
        description = "Delete an user."
        model = User
        field_name = "user"
        field_type = types.User

    @classmethod
    @gql_lock(name="DeleteUser", attr="id")
    @staff_required
    @has_perm("accounts.delete_user")
    def perform_mutation(cls, root, info, **kwargs):
        return super().perform_mutation(root, info, **kwargs)


class CreateComment(mutations.ModelMutation):
    """Create comment."""

    class Arguments:
        input = inputs.CreateCommentInput(
            required=True, description="Create comment input."
        )

    class Meta:
        description = "Create comment."
        model = models.Note
        exclude = (
            "id",
            "user",
            "username",
        )
        field_name = "comment"
        field_type = types.Comment

    @classmethod
    @gql_lock(name="CreateComment")
    @transaction.atomic
    def perform_mutation(cls, root, info, **kwargs):
        input = kwargs["input"]
        user_kwargs = {
            "instance": models.User(
                username=f"user.{unique_id(11)}", password="...", is_active=False
            ),
            "input": input["user"],
            "input_cls": cls.Arguments.input.user,
        }
        input["user"] = super().perform_mutation(root, info, **user_kwargs)
        return super().perform_mutation(root, info, **kwargs)


class UpdateComment(mutations.ModelMutation):
    """Update comment."""

    class Arguments:
        id = graphene.ID(required=True, description="Comment ID.")
        input = inputs.UpdateCommentInput(
            required=True, description="Update comment input."
        )

    class Meta:
        description = "Update comment."
        model = models.Note
        exclude = (
            "user",
            "username",
        )
        field_name = "comment"
        field_type = types.Comment

    @classmethod
    @gql_lock(name="UpdateComment", attr="id")
    @transaction.atomic
    def perform_mutation(cls, root, info, **kwargs):
        user_input = kwargs["input"].pop("user")
        instance = super().perform_mutation(root, info, **kwargs)
        user_kwargs = {
            "instance": instance.user,
            "input": user_input,
            "input_cls": cls.Arguments.input.user,
        }
        instance.user = super().perform_mutation(root, info, **user_kwargs)
        return instance


class DeleteComment(mutations.ModelDeleteMutation):
    """Delete comment."""

    class Arguments:
        id = graphene.ID(required=True, description="Comment ID.")

    class Meta:
        description = "Delete comment."
        model = models.Note
        field_name = "comment"
        field_type = types.Comment

    @classmethod
    @gql_lock(name="DeleteComment", attr="id")
    @transaction.atomic
    def perform_mutation(cls, root, info, **kwargs):
        instance = super().perform_mutation(root, info, **kwargs)
        id = instance.user.id
        instance.user.delete()
        instance.user.id = id
        return instance


class UserMutation:
    """User mutation type"""

    enable_t_f_a = EnableTFA.Field()
    disable_t_f_a = DisableTFA.Field()

    signin = Signin.Field()
    social_signin = SocialSignin.Field()
    refresh_token = RefreshToken.Field()

    check_user = CheckUser.Field()

    send_signup_token = SendSignupToken.Field()
    check_signup_token = CheckSignupToken.Field()
    signup = Signup.Field()

    change_password = ChangePassword.Field()

    send_password_token = SendPasswordToken.Field()
    check_password_token = CheckPasswordToken.Field()
    reset_password = ResetPassword.Field()

    update_me = UpdateMe.Field()

    create_user = CreateUser.Field()
    update_user = UpdateUser.Field()
    delete_user = DeleteUser.Field()


class NoteMutation:
    """Note mutation type"""

    create_note = CreateNote.Field()
    update_note = UpdateNote.Field()
    delete_note = DeleteNote.Field()


class CommentMutation:
    """Comment mutation type"""

    create_comment = CreateComment.Field()
    update_comment = UpdateComment.Field()
    delete_comment = DeleteComment.Field()


class Mutation(UserMutation, NoteMutation, CommentMutation):
    """Mutation type"""

    pass
