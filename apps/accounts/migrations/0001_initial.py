# Generated by Django 3.1.4 on 2021-01-01 16:03

import django.contrib.auth.models
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import apps.accounts.models
import apps.common.defaults
import apps.common.validators


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "id",
                    models.CharField(
                        default=apps.common.defaults.b64_id,
                        editable=False,
                        max_length=22,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="first name"
                    ),
                ),
                (
                    "middle_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="middle name"
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True, max_length=150, verbose_name="last name"
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        max_length=200,
                        unique=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                code="invalid_username",
                                message="Enter a valid username.",
                                regex="^[a-zA-Z0-9-_.@]{1,200}$",
                            )
                        ],
                        verbose_name="username",
                    ),
                ),
                ("password", models.CharField(max_length=150, verbose_name="password")),
                (
                    "email",
                    models.EmailField(
                        blank=True, max_length=254, verbose_name="email address"
                    ),
                ),
                (
                    "birthday",
                    models.DateField(blank=True, null=True, verbose_name="birthday"),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=15, verbose_name="phone number"
                    ),
                ),
                (
                    "avatar",
                    models.ImageField(
                        blank=True,
                        max_length=200,
                        upload_to=apps.accounts.models.avatar_upload_to,
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                ["png", "jpg"]
                            ),
                            apps.common.validators.FileSizeValidator(max_size=1024.0),
                        ],
                        verbose_name="avatar",
                    ),
                ),
                (
                    "renewed",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="renewed"
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
                "db_table": "accounts_user",
                "ordering": ("pk",),
            },
            managers=[
                ("objects", django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="UserPermission",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=apps.common.defaults.b64_id,
                        editable=False,
                        max_length=22,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "permission",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="auth.permission",
                        verbose_name="permission",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
            ],
            options={
                "verbose_name": "user permission",
                "verbose_name_plural": "user permissions",
                "db_table": "accounts_user_permissions",
                "unique_together": {("user", "permission")},
            },
        ),
        migrations.CreateModel(
            name="UserGroup",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=apps.common.defaults.b64_id,
                        editable=False,
                        max_length=22,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to="auth.group",
                        verbose_name="group",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="+",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
            ],
            options={
                "verbose_name": "user group",
                "verbose_name_plural": "user groups",
                "db_table": "accounts_user_groups",
                "unique_together": {("user", "group")},
            },
        ),
        migrations.CreateModel(
            name="Note",
            fields=[
                (
                    "id",
                    models.CharField(
                        default=apps.common.defaults.b64_id,
                        editable=False,
                        max_length=22,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(max_length=500, verbose_name="content")),
                (
                    "created",
                    models.DateTimeField(auto_now_add=True, verbose_name="created"),
                ),
                (
                    "modified",
                    models.DateTimeField(auto_now=True, verbose_name="modified"),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notes",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="user",
                    ),
                ),
            ],
            options={
                "verbose_name": "note",
                "verbose_name_plural": "notes",
                "db_table": "accounts_note",
                "ordering": ("pk",),
            },
        ),
        migrations.AddField(
            model_name="user",
            name="groups",
            field=models.ManyToManyField(
                blank=True,
                help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                related_name="user_set",
                related_query_name="user",
                through="accounts.UserGroup",
                to="auth.Group",
                verbose_name="groups",
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="user_permissions",
            field=models.ManyToManyField(
                blank=True,
                help_text="Specific permissions for this user.",
                related_name="user_set",
                related_query_name="user",
                through="accounts.UserPermission",
                to="auth.Permission",
                verbose_name="user permissions",
            ),
        ),
    ]
