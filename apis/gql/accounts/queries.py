import graphene
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _

from apis.gql.accounts import types
from apis.gql.auth import auth_required, has_perm, staff_required
from apps.common.utils import get_object
from apps.gql.fields import ModelCursorConnectionField
from apps.gql.utils import id_from_global_id, node_from_global_id

User = get_user_model()


class UserQuery:
    """User query type"""

    me = graphene.Field(types.User, description="Me.")

    users = ModelCursorConnectionField(types.User, description="Users.")
    user = graphene.Field(
        types.User, id=graphene.ID(), username=graphene.String(), description="User."
    )

    @classmethod
    @auth_required
    def resolve_me(cls, root, info):
        return info.context.user

    @classmethod
    @staff_required
    @has_perm("accounts.view_user")
    def resolve_users(cls, root, info, **kwargs):
        return types.User._meta.model.objects.defer(
            "password",
            "renewed",
            "is_active",
            "is_staff",
            "is_superuser",
            "tfa_secret",
            "tfa_last_code",
        )

    @classmethod
    @staff_required
    @has_perm("accounts.view_user")
    def resolve_user(cls, root, info, id=None, username=None):
        if id:
            return node_from_global_id(info, id, only_type=types.User)
        if username:
            return get_object(types.User._meta.model, username=username)


class NoteQuery:
    """Note query type"""

    notes = ModelCursorConnectionField(types.Note, description="Notes.")
    note = graphene.Field(
        types.Note, id=graphene.ID(required=True), description="Note."
    )

    user_notes = ModelCursorConnectionField(
        types.Note,
        user_id=graphene.ID(),
        username=graphene.String(),
        description="User notes.",
    )

    @classmethod
    @auth_required
    def resolve_notes(cls, root, info, **kwargs):
        return info.context.user.notes

    @classmethod
    @auth_required
    def resolve_note(cls, root, info, id):
        note = node_from_global_id(info, id, only_type=types.Note)

        if note and note.user_id != info.context.user.pk:
            raise ValidationError(
                {
                    "perm": _("Permission denied."),
                }
            )
        return note

    @classmethod
    @staff_required
    @has_perm("accounts.view_note")
    def resolve_user_notes(cls, root, info, user_id=None, username=None, **kwargs):
        qs = types.Note._meta.model.objects

        if user_id:
            pk = id_from_global_id(user_id)
            qs = qs.filter(user=pk) if pk else qs.none()
        elif username:
            qs = qs.filter(user__username=username)
        else:
            qs = qs.none()
        return qs


class CommentQuery:
    """Comment query type"""

    comments = ModelCursorConnectionField(types.Comment, description="Comments.")
    comment = graphene.Field(
        types.Comment, id=graphene.ID(required=True), description="Comment."
    )

    @classmethod
    def resolve_comments(cls, root, info, **kwargs):
        prefetch_user = Prefetch(
            "user", queryset=User.objects.only("first_name", "last_name", "email")
        )
        return types.Comment._meta.model.objects.prefetch_related(prefetch_user)

    @classmethod
    def resolve_comment(cls, root, info, id):
        return node_from_global_id(info, id, only_type=types.Comment)


class Query(UserQuery, NoteQuery, CommentQuery):
    """Query type"""

    pass
