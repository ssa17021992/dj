import graphene
from django.contrib.auth import get_user_model

from apis.gql.accounts import filters
from apis.gql.common.fields import Image
from apps.accounts import models
from apps.gql.fields import DateTimeTZ
from apps.gql.types import ModelObjectType


class Note(ModelObjectType, interfaces=(graphene.Node,)):
    """Note type"""

    created = DateTimeTZ(required=True)
    modified = DateTimeTZ(required=True)

    class Meta:
        model = models.Note
        exclude = ("user",)
        filterset_class = filters.NoteFilter

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset


class User(ModelObjectType, interfaces=(graphene.Node,)):
    """User type"""

    avatar = Image()

    last_login = DateTimeTZ()
    date_joined = DateTimeTZ(required=True)

    tfa_active = graphene.Boolean(description="TFA authentication active.")

    class Meta:
        model = get_user_model()
        exclude = (
            "password",
            "renewed",
            "notes",
            "is_active",
            "is_staff",
            "is_superuser",
            "tfa_secret",
            "tfa_last_code",
        )
        filterset_class = filters.UserFilter

    @classmethod
    def get_queryset(cls, queryset, info):
        return queryset

    @classmethod
    def resolve_tfa_active(cls, root, info):
        return root.tfa_active


class Person(ModelObjectType, interfaces=(graphene.Node,)):
    """Person type"""

    class Meta:
        model = get_user_model()
        fields = (
            "first_name",
            "last_name",
            "email",
        )


class Comment(ModelObjectType, interfaces=(graphene.Node,)):
    """Comment type"""

    user = graphene.Field(Person, required=True)
    created = DateTimeTZ(required=True)

    class Meta:
        model = models.Note
        fields = (
            "content",
            "user",
            "created",
        )
        filterset_class = filters.CommentFilter
