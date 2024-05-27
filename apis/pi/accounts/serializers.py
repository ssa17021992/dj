from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from apis.pi import mixins
from apps.accounts.auth.exceptions import AuthError
from apps.accounts.auth.utils import get_auth_backend
from apps.accounts.models import Note
from apps.accounts.utils import signup_token
from apps.common.utils import exec_task, get_object, to_object, unique_id

User = get_user_model()

password_validator = RegexValidator(
    regex="^.{1,200}$", message=_("Enter a valid password."), code="invalid_password"
)


class EnableTFASerializer(serializers.Serializer):
    """Enable TFA serializer."""

    password = serializers.CharField(max_length=200)

    def validate(self, attrs):
        user = self.context["request"].user
        if user.tfa_active:
            raise serializers.ValidationError(
                {
                    "tfa_secret": _("The TFA authentication is already enabled."),
                }
            )
        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError(
                {
                    "password": _("Wrong password."),
                }
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        user.enable_tfa()
        return user


class DisableTFASerializer(serializers.Serializer):
    """Disable TFA serializer."""

    password = serializers.CharField(max_length=200)
    tfa_code = serializers.CharField(max_length=6)

    def validate(self, attrs):
        user = self.context["request"].user
        if not user.tfa_active:
            raise serializers.ValidationError(
                {
                    "tfa_secret": _("The TFA authentication is not enabled."),
                }
            )
        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError(
                {
                    "password": _("Wrong password."),
                }
            )
        if not user.check_tfa_code(attrs["tfa_code"]):
            raise serializers.ValidationError(
                {
                    "tfa_code": _("Wrong TFA authentication code."),
                }
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        user.disable_tfa()
        return user


class CheckUserSerializer(serializers.Serializer):
    """Check user serializer"""

    username = serializers.CharField(max_length=200)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError(_("Username already in use."))
        return value

    def create(self, validated_data):
        return to_object(validated_data)


class SendSignupTokenSerializer(serializers.Serializer):
    """Send signup token serializer"""

    username = serializers.CharField(max_length=200)
    email = serializers.EmailField(allow_blank=True, allow_null=True)
    phone = serializers.CharField(max_length=15, allow_blank=True, allow_null=True)

    def create(self, validated_data):
        user = to_object(validated_data)
        token = signup_token(user)
        exec_task(
            "accounts.send_signup_mail",
            args=(
                token,
                user.email,
            ),
        )
        return user


class SignupSerializer(serializers.ModelSerializer):
    """Signup serializer"""

    password = serializers.CharField(
        max_length=200,
        validators=[
            password_validator,
        ],
    )

    def validate(self, attrs):
        user = self.context["request"].user
        if User.objects.filter(username=user.username).exists():
            raise serializers.ValidationError({"token": _("Invalid token.")})
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        instance = super().create(validated_data)

        instance.username = user.username
        instance.email = getattr(user, "email", "")
        instance.phone = getattr(user, "phone", "")

        instance.set_password(validated_data["password"])
        instance.save(
            update_fields=[
                "username",
                "email",
                "phone",
                "password",
            ]
        )
        return instance

    class Meta:
        model = User
        exclude = (
            "username",
            "email",
            "phone",
            "avatar",
            "date_joined",
            "groups",
            "is_active",
            "is_staff",
            "is_superuser",
            "renewed",
            "user_permissions",
        )


class SigninSerializer(serializers.Serializer):
    """Signin serializer"""

    username = serializers.CharField(max_length=200)
    password = serializers.CharField(max_length=200)
    tfa_code = serializers.CharField(max_length=6, allow_blank=True, required=False)

    def validate_username(self, value):
        user = get_object(User, username=value)
        if not user:
            raise serializers.ValidationError(_("User does not exist."))

        if not user.is_active:
            raise serializers.ValidationError(_("User inactive."))

        self.instance = user
        return value

    def validate(self, attrs):
        user = self.instance
        if not user.check_password(attrs["password"]):
            raise serializers.ValidationError(
                {
                    "password": _("Wrong password."),
                }
            )
        if user.tfa_active:
            if not attrs.get("tfa_code"):
                raise serializers.ValidationError(
                    {
                        "tfa_code": _("This field is required."),
                    }
                )
            if not user.check_tfa_code(attrs["tfa_code"]):
                raise serializers.ValidationError(
                    {
                        "tfa_code": _("Wrong TFA authentication code."),
                    }
                )
        return attrs

    def update(self, instance, validated_data):
        instance.update_last_login()
        return instance


class SocialSigninSerializer(serializers.Serializer):
    """Social signin serializer"""

    social = serializers.CharField(max_length=10)
    token = serializers.CharField(max_length=300)
    tfa_code = serializers.CharField(max_length=6, allow_blank=True, required=False)

    def validate_social(self, value):
        socials = (
            "facebook",
            "google",
        )

        if settings.USE_DUMMY:
            socials = ("dummy",) + socials
        if value not in socials:
            raise serializers.ValidationError(
                _("This social network is not implemented.")
            )
        return value

    def validate(self, attrs):
        auth_backend = get_auth_backend(attrs["social"])
        try:
            user = auth_backend.signin(attrs["token"])
        except AuthError as e:
            raise serializers.ValidationError({e.field: e.message})
        if not user.is_active:
            raise serializers.ValidationError(
                {
                    "username": _("User inactive."),
                }
            )
        if user.tfa_active:
            if not attrs.get("tfa_code"):
                raise serializers.ValidationError(
                    {
                        "tfa_code": _("This field is required."),
                    }
                )
            if not user.check_tfa_code(attrs["tfa_code"]):
                raise serializers.ValidationError(
                    {
                        "tfa_code": _("Wrong TFA authentication code."),
                    }
                )

        self.instance = user
        return attrs

    def update(self, instance, validated_data):
        instance.update_last_login()
        return instance


class CreateUserSerializer(serializers.ModelSerializer):
    """Create user serializer"""

    password = serializers.CharField(
        max_length=200,
        validators=[
            password_validator,
        ],
    )

    def create(self, validated_data):
        instance = User(**validated_data)
        instance.set_password(validated_data["password"])
        instance.save()
        return instance

    class Meta:
        model = User
        fields = (
            "username",
            "password",
        )


class ListUserSerializer(mixins.QueryFieldsMixin, serializers.ModelSerializer):
    """List user serializer"""

    tfa_active = serializers.BooleanField()

    class Meta:
        model = User
        exclude = (
            "date_joined",
            "groups",
            "is_active",
            "is_staff",
            "is_superuser",
            "password",
            "renewed",
            "user_permissions",
            "tfa_secret",
            "tfa_last_code",
        )


class UpdateUserSerializer(serializers.ModelSerializer):
    """Update user serializer"""

    def update(self, instance, validated_data):
        if validated_data:
            for field, value in validated_data.items():
                setattr(instance, field, value)
            instance.save(update_fields=validated_data)
        return instance

    class Meta:
        model = User
        fields = (
            "first_name",
            "middle_name",
            "last_name",
            "birthday",
        )


class ChangeAvatarSerializer(serializers.ModelSerializer):
    """Change avatar serializer"""

    class Meta:
        model = User
        fields = ("avatar",)
        extra_kwargs = {
            "avatar": {
                "allow_null": False,
            },
        }


class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""

    current = serializers.CharField(max_length=200)
    password = serializers.CharField(
        max_length=200,
        validators=[
            password_validator,
        ],
    )
    expire_keys = serializers.BooleanField()

    def validate_current(self, value):
        if not self.instance.check_password(value):
            raise serializers.ValidationError(_("Wrong password."))
        return value

    def validate(self, attrs):
        if attrs["current"] == attrs["password"]:
            raise serializers.ValidationError(
                {
                    "password": _("Current and new password cannot be same."),
                }
            )
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(
            validated_data["password"], expire_keys=validated_data["expire_keys"]
        )
        instance.save(
            update_fields=[
                "password",
                "renewed",
            ]
        )
        return instance


class SendPasswordTokenSerializer(serializers.Serializer):
    """Send password token serializer"""

    username = serializers.CharField(max_length=200)

    def validate_username(self, value):
        user = get_object(User, username=value)
        if not user:
            raise serializers.ValidationError(_("User does not exist."))

        self.context["user"] = user
        return value

    def create(self, validated_data):
        user = self.context["user"]
        token = user.get_passwd_token()
        exec_task(
            "accounts.send_passwd_reset_mail",
            args=(
                token,
                user.username,
                user.email,
            ),
        )
        return to_object({})


class ResetPasswordSerializer(serializers.Serializer):
    """Reset password serializer"""

    password = serializers.CharField(
        max_length=200,
        validators=[
            password_validator,
        ],
    )

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"], expire_keys=True)
        instance.save(
            update_fields=[
                "password",
                "renewed",
            ]
        )
        return instance


class CreateNoteSerializer(serializers.ModelSerializer):
    """Create note serializer"""

    def create(self, validated_data):
        user = self.context["request"].user
        return user.notes.create(**validated_data)

    class Meta:
        model = Note
        fields = ("content",)


class ListNoteSerializer(mixins.QueryFieldsMixin, serializers.ModelSerializer):
    """List note serializer"""

    class Meta:
        model = Note
        fields = (
            "id",
            "content",
            "created",
            "modified",
        )


class UpdateNoteSerializer(serializers.ModelSerializer):
    """Update note serializer"""

    def update(self, instance, validated_data):
        content = validated_data.get("content", instance.content)
        if instance.content != content:
            instance.content = content
            instance.save(
                update_fields=[
                    "content",
                    "modified",
                ]
            )
        return instance

    class Meta:
        model = Note
        fields = ("content",)


class CreatePersonSerializer(serializers.ModelSerializer):
    """Create person serializer"""

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
        )


class ListPersonSerializer(serializers.ModelSerializer):
    """List person serializer"""

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
        )


class UpdatePersonSerializer(serializers.ModelSerializer):
    """Update person serializer"""

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
        )


class CreateCommentSerializer(serializers.ModelSerializer):
    """Create comment serializer"""

    user = CreatePersonSerializer(many=False)

    @transaction.atomic
    def create(self, validated_data):
        validated_data["user"] = User.objects.create(
            username=f"user.{unique_id(11)}",
            password="...",
            is_active=False,
            **validated_data["user"],
        )
        return Note.objects.create(**validated_data)

    class Meta:
        model = Note
        fields = (
            "content",
            "user",
        )


class ListCommentSerializer(mixins.QueryFieldsMixin, serializers.ModelSerializer):
    """List comment serializer"""

    user = ListPersonSerializer(many=False)

    class Meta:
        model = Note
        fields = (
            "id",
            "content",
            "user",
            "created",
            "modified",
        )


class UpdateCommentSerializer(serializers.ModelSerializer):
    """Update comment serializer"""

    user = UpdatePersonSerializer(many=False)

    @transaction.atomic
    def update(self, instance, validated_data):
        content = validated_data.get("content", instance.content)
        user = validated_data.get("user")

        if content != instance.content:
            instance.content = content
            instance.save(update_fields=["content"])
        if user:
            for field, value in user.items():
                setattr(instance.user, field, value)
            instance.user.save(update_fields=user)

        return instance

    class Meta:
        model = Note
        fields = (
            "content",
            "user",
        )
