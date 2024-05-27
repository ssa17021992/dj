import django_filters as filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.accounts.models import Note


class UserFilter(filters.FilterSet):
    """User filter."""

    search = filters.CharFilter(method="filter_search")
    # order_by = filters.OrderingFilter(
    #    fields=(
    #        ("username", "username",),
    #        ("email", "email",),
    #        ("date_joined", "date_joined",),
    #    )
    # )

    def filter_search(self, queryset, name, value):
        if len(value) < 3:
            return queryset
        return queryset.filter(
            Q(username__startswith=value)
            | Q(email__startswith=value)
            | Q(phone__startswith=value)
            | Q(first_name__startswith=value)
            | Q(middle_name__startswith=value)
            | Q(last_name__startswith=value)
        )

    class Model:
        model = get_user_model()
        fields = []


class NoteFilter(filters.FilterSet):
    """Note filter."""

    search = filters.CharFilter(method="filter_search")
    # order_by = filters.OrderingFilter(
    #    fields=(
    #        ("created", "created",),
    #        ("modified", "modified",),
    #    )
    # )

    def filter_search(self, queryset, name, value):
        return queryset.filter(content__icontains=value)

    class Meta:
        model = Note
        fields = []


class CommentFilter(filters.FilterSet):
    """Comment filter."""

    search = filters.CharFilter(method="filter_search")
    # order_by = filters.OrderingFilter(
    #    fields=(
    #        ("created", "created",),
    #        ("modified", "modified",),
    #    )
    # )

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(content__icontains=value)
            | Q(user__email__icontains=value)
            | Q(user__first_name__icontains=value)
            | Q(user__last_name__icontains=value)
        )

    class Meta:
        model = Note
        fields = []
