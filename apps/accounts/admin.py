from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as AuthUserAdmin
from django.contrib.auth.models import Permission
from django.utils.translation import gettext_lazy as _

from apps.accounts.models import Note

User = get_user_model()


class UserGroupInline(admin.StackedInline):
    """User group inline"""

    model = User.groups.through
    extra = 0
    autocomplete_fields = ("group",)


class UserPermissionInline(admin.StackedInline):
    """User permission inline"""

    model = User.user_permissions.through
    extra = 0
    autocomplete_fields = ("permission",)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """Permission admin"""

    list_display = ("name",)
    search_fields = ("name",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(User)
class UserAdmin(AuthUserAdmin):
    """User admin"""

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "middle_name",
                    "last_name",
                    "email",
                    "phone",
                    "birthday",
                    "avatar",
                )
            },
        ),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser")}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = (
        "username",
        "email",
        "is_active",
        "date_joined",
    )
    readonly_fields = (
        "last_login",
        "date_joined",
    )
    filter_horizontal = ()

    inlines = [
        UserGroupInline,
        UserPermissionInline,
    ]


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    """Note admin"""

    list_display = (
        "id",
        "short_content",
        "created",
        "modified",
    )
    readonly_fields = (
        "content",
        "user",
        "created",
        "modified",
    )
    search_fields = ("content",)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
