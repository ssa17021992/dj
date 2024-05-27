import base64
import io

import pyotp
import qrcode
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator, RegexValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts.utils import auth_refresh_token, auth_token, passwd_token
from apps.common.models import Model
from apps.common.validators import FileSizeValidator


def avatar_upload_to(user, filename):
    return f"files/f-{user.id}/avatar/{filename}"


class UserGroup(Model):
    """User group model"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    group = models.ForeignKey(
        "auth.Group",
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name=_("group"),
    )

    class Meta:
        db_table = "accounts_user_groups"
        verbose_name = _("user group")
        verbose_name_plural = _("user groups")
        unique_together = (("user", "group"),)


class UserPermission(Model):
    """User permission model"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )
    permission = models.ForeignKey(
        "auth.Permission",
        related_name="+",
        on_delete=models.CASCADE,
        verbose_name=_("permission"),
    )

    class Meta:
        db_table = "accounts_user_permissions"
        verbose_name = _("user permission")
        verbose_name_plural = _("user permissions")
        unique_together = (("user", "permission"),)


class User(Model, AbstractUser):
    """User model"""

    first_name = models.CharField(
        max_length=150, blank=True, verbose_name=_("first name")
    )
    middle_name = models.CharField(
        max_length=150, blank=True, verbose_name=_("middle name")
    )
    last_name = models.CharField(
        max_length=150, blank=True, verbose_name=_("last name")
    )

    username = models.CharField(
        max_length=200,
        unique=True,
        validators=[
            RegexValidator(
                regex="^[a-zA-Z0-9-_.@]{1,200}$",
                message=_("Enter a valid username."),
                code="invalid_username",
            ),
        ],
        verbose_name=_("username"),
    )

    password = models.CharField(max_length=150, verbose_name=_("password"))

    email = models.EmailField(blank=True, verbose_name=_("email address"))
    birthday = models.DateField(null=True, blank=True, verbose_name=_("birthday"))
    phone = models.CharField(max_length=15, blank=True, verbose_name=_("phone number"))

    avatar = models.ImageField(
        max_length=200,
        blank=True,
        upload_to=avatar_upload_to,
        validators=[
            FileExtensionValidator(["png", "jpg"]),
            FileSizeValidator(max_size=1024.0),  # Limited to 1 mb.
        ],
        verbose_name=_("avatar"),
    )

    renewed = models.DateTimeField(default=timezone.now, verbose_name=_("renewed"))

    groups = models.ManyToManyField(
        "auth.Group",
        through="accounts.UserGroup",
        through_fields=("user", "group"),
        verbose_name=_("groups"),
        blank=True,
        help_text=_(
            "The groups this user belongs to. A user will get all permissions "
            "granted to each of their groups."
        ),
        related_name="user_set",
        related_query_name="user",
    )
    user_permissions = models.ManyToManyField(
        "auth.Permission",
        through="accounts.UserPermission",
        through_fields=("user", "permission"),
        verbose_name=_("user permissions"),
        blank=True,
        help_text=_("Specific permissions for this user."),
        related_name="user_set",
        related_query_name="user",
    )

    tfa_secret = models.CharField(
        max_length=32, blank=True, verbose_name=_("TFA secret")
    )
    tfa_last_code = models.CharField(
        max_length=6, blank=True, verbose_name=_("TFA last code")
    )

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email"]

    @property
    def tfa_active(self):
        return bool(self.tfa_secret)

    @property
    def totp(self):
        """Get TOTP client."""
        return pyotp.TOTP(self.tfa_secret)

    @property
    def totp_qr_code(self):
        """Get TOTP provisioning URI as QR code image."""
        buffer = io.BytesIO()
        qr = qrcode.QRCode()
        qr.add_data(self.totp.provisioning_uri(self.username, "App"))
        qr.make(fit=True)
        qr.make_image().save(buffer, format="PNG")
        b64 = base64.b64encode(buffer.getvalue()).decode()
        return "data:image/png;base64,%s" % b64

    def enable_tfa(self):
        """Enable Two Factor Authentication."""
        self.tfa_secret = pyotp.random_base32()
        self.save(update_fields=["tfa_secret"])
        return self.tfa_secret

    def disable_tfa(self):
        """Disable Two Factor Authentication."""
        self.tfa_secret = ""
        self.save(update_fields=["tfa_secret"])
        return self.tfa_secret

    def get_tfa_code(self):
        """Get Two Factor Authentication code."""
        return self.totp.now()

    def check_tfa_code(self, code):
        """Check Two Factor Authentication code."""
        is_valid = self.totp.verify(code) if self.tfa_last_code != code else False
        if is_valid:
            self.tfa_last_code = code
            self.save(update_fields=["tfa_last_code"])
        return is_valid

    def get_token(self):
        """Get auth token."""
        return auth_token(self)

    def get_refresh_token(self):
        """Get refresh token."""
        return auth_refresh_token(self)

    def get_passwd_token(self):
        """Get password reset token."""
        return passwd_token(self)

    def set_password(self, password, expire_keys=False):
        """Change password."""
        super().set_password(password)
        if expire_keys:
            self.expire_keys(commit=False)

    def expire_keys(self, commit=True):
        """Expire all generated auth and refresh tokens."""
        self.renewed = timezone.now()
        if commit:
            self.save(update_fields=["renewed"])

    def update_last_login(self, commit=True):
        """Update last login (datetime)."""
        self.last_login = timezone.now()
        if commit:
            self.save(update_fields=["last_login"])

    @property
    def rnd(self):
        return int(self.renewed.timestamp())

    def __str__(self):
        return self.username

    class Meta:
        db_table = "accounts_user"
        verbose_name = _("user")
        verbose_name_plural = _("users")
        ordering = ("pk",)


class Note(Model):
    """Note model"""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="notes",
        on_delete=models.CASCADE,
        verbose_name=_("user"),
    )

    content = models.TextField(max_length=500, verbose_name=_("content"))

    created = models.DateTimeField(auto_now_add=True, verbose_name=_("created"))
    modified = models.DateTimeField(auto_now=True, verbose_name=_("modified"))

    @property
    def short_content(self):
        if len(self.content) > 30:
            return "%s..." % self.content[:30]
        return self.content

    class Meta:
        db_table = "accounts_note"
        verbose_name = _("note")
        verbose_name_plural = _("notes")
        ordering = ("pk",)
