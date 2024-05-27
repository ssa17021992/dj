from collections import OrderedDict
from datetime import timezone as tz
from functools import partial

import graphene
from django.core.exceptions import ValidationError
from django.db.models.query import QuerySet
from django.utils import timezone
from graphene import NonNull
from graphene.relay import ConnectionField as RelayConnectionField
from graphene.relay.connection import connection_adapter, page_info_adapter
from graphene.types import Field, List
from graphene.types.argument import to_arguments
from graphene_django.filter.fields import (  # noqa
    DjangoFilterConnectionField as ModelConnectionField,
)
from graphene_django.filter.utils import (
    get_filtering_args_from_filterset,
    get_filterset_class,
)
from graphene_django.settings import graphene_settings
from graphene_django.utils import maybe_queryset
from promise import Promise

from apps.gql.array_connection import connection_from_objects, connection_from_queryset
from apps.gql.types import ModelObjectType
from apps.gql.utils import to_snake_case


def validate_first_and_last(info, enforce_first_or_last, max_limit, **kwargs):
    first = kwargs.get("first")
    last = kwargs.get("last")
    offset = kwargs.get("offset")
    before = kwargs.get("before")

    if enforce_first_or_last:
        assert first or last, (
            "You must provide a `first` or `last` "
            "value to properly paginate the `{}` connection."
        ).format(info.field_name)

    if max_limit:
        if first:
            assert first <= max_limit, (
                "Requesting {} records on the `{}` "
                "connection exceeds the `first` limit of {} records."
            ).format(first, info.field_name, max_limit)
            kwargs["first"] = min(first, max_limit)

        if last:
            assert last <= max_limit, (
                "Requesting {} records on the `{}` "
                "connection exceeds the `last` limit of {} records."
            ).format(last, info.field_name, max_limit)
            kwargs["last"] = min(last, max_limit)

    if offset is not None:
        assert before is None, (
            "You can't provide a `before` value at the same time "
            "as an `offset` value to properly paginate the `{}` connection."
        ).format(info.field_name)


class DjangoListField(Field):
    def __init__(self, _type, *args, **kwargs):
        if isinstance(_type, NonNull):
            _type = _type.of_type

        super().__init__(List(NonNull(_type)), *args, **kwargs)

        assert issubclass(
            self._underlying_type, ModelObjectType
        ), "DjangoListField only accepts DjangoObjectType types"

    @property
    def _underlying_type(self):
        _type = self._type
        while hasattr(_type, "of_type"):
            _type = _type.of_type
        return _type

    @property
    def model(self):
        return self._underlying_type._meta.model

    def get_manager(self):
        return self.model._default_manager

    @staticmethod
    def list_resolver(
        django_object_type, resolver, default_manager, root, info, **args
    ):
        queryset = maybe_queryset(resolver(root, info, **args))
        if queryset is None:
            queryset = maybe_queryset(default_manager)

        if isinstance(queryset, QuerySet):
            queryset = maybe_queryset(django_object_type.get_queryset(queryset, info))
        return queryset

    def wrap_resolve(self, parent_resolver):
        _type = self.type
        if isinstance(_type, NonNull):
            _type = _type.of_type
        django_object_type = _type.of_type.of_type
        return partial(
            self.list_resolver, django_object_type, parent_resolver, self.get_manager()
        )


class DjangoCursorConnectionField(RelayConnectionField):
    def __init__(self, *args, **kwargs):
        self.on = kwargs.pop("on", False)
        self.enforce_first_or_last = kwargs.pop(
            "enforce_first_or_last",
            graphene_settings.RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST,
        )
        self.max_limit = kwargs.pop(
            "max_limit", graphene_settings.RELAY_CONNECTION_MAX_LIMIT
        )
        self.cursor_field = kwargs.pop("cursor_field", "id")
        super().__init__(*args, **kwargs)

    @property
    def type(self):
        _type = super(RelayConnectionField, self).type
        non_null = False
        if isinstance(_type, NonNull):
            _type = _type.of_type
            non_null = True

        assert issubclass(
            _type, ModelObjectType
        ), "DjangoConnectionField only accepts DjangoObjectType types"
        assert _type._meta.connection, "The type {} doesn't have a connection".format(
            _type.__name__
        )
        connection_type = _type._meta.connection

        if non_null:
            return NonNull(connection_type)
        return connection_type

    @property
    def connection_type(self):
        return self.type.of_type if isinstance(self.type, NonNull) else self.type

    @property
    def node_type(self):
        return self.connection_type._meta.node

    @property
    def model(self):
        return self.node_type._meta.model

    def get_manager(self):
        return getattr(self.model, self.on) if self.on else self.model._default_manager

    @classmethod
    def resolve_queryset(cls, connection, queryset, info, args):
        return connection._meta.node.get_queryset(queryset, info)

    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit, cursor_field):
        limit = min(args.get("first") or args.get("last"), max_limit)
        connection = connection_from_queryset(
            iterable,
            limit,
            args,
            cursor_field,
            connection_type=partial(connection_adapter, connection),
            edge_type=connection.Edge,
            page_info_type=page_info_adapter,
        )
        connection.iterable = iterable
        connection.length = limit
        return connection

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection,
        default_manager,
        queryset_resolver,
        enforce_first_or_last,
        max_limit,
        cursor_field,
        root,
        info,
        **kwargs,
    ):
        validate_first_and_last(info, enforce_first_or_last, max_limit, **kwargs)

        iterable = resolver(root, info, **kwargs)
        if iterable is None:
            iterable = default_manager

        iterable = queryset_resolver(connection, iterable, info, kwargs)
        on_resolve = partial(
            cls.resolve_connection,
            connection,
            kwargs,
            iterable,
            max_limit,
            cursor_field,
        )

        if Promise.is_thenable(iterable):
            return Promise.resolve().then(on_resolve)
        return on_resolve()

    def wrap_resolve(self, parent_resolver):
        return partial(
            self.connection_resolver,
            parent_resolver,
            self.connection_type,
            self.get_manager(),
            self.get_queryset_resolver(),
            self.enforce_first_or_last,
            self.max_limit,
            self.cursor_field,
        )

    def get_queryset_resolver(self):
        return self.resolve_queryset


class DjangoFilterCursorConnectionField(DjangoCursorConnectionField):
    def __init__(
        self,
        type,
        fields=None,
        order_by=None,
        extra_filter_meta=None,
        filterset_class=None,
        *args,
        **kwargs,
    ):
        self._fields = fields
        self._provided_filterset_class = filterset_class
        self._filterset_class = None
        self._filtering_args = None
        self._extra_filter_meta = extra_filter_meta
        self._base_args = None
        super().__init__(type, *args, **kwargs)

    @property
    def args(self):
        return to_arguments(self._base_args or OrderedDict(), self.filtering_args)

    @args.setter
    def args(self, args):
        self._base_args = args

    @property
    def filterset_class(self):
        if not self._filterset_class:
            meta = {
                "model": self.model,
                "fields": self._fields or self.node_type._meta.filter_fields,
            }
            if self._extra_filter_meta:
                meta.update(self._extra_filter_meta)

            filterset_class = self._provided_filterset_class or (
                self.node_type._meta.filterset_class
            )
            self._filterset_class = get_filterset_class(filterset_class, **meta)
        return self._filterset_class

    @property
    def filtering_args(self):
        if not self._filtering_args:
            self._filtering_args = get_filtering_args_from_filterset(
                self.filterset_class, self.node_type
            )
        return self._filtering_args

    @classmethod
    def resolve_queryset(
        cls, connection, iterable, info, args, filtering_args, filterset_class
    ):
        def filter_kwargs():
            kwargs = {}
            for k, v in args.items():
                if k in filtering_args:
                    if k == "order_by" and v is not None:
                        v = to_snake_case(v)
                    kwargs[k] = v
            return kwargs

        qs = super(DjangoFilterCursorConnectionField, cls).resolve_queryset(
            connection, iterable, info, args
        )

        filterset = filterset_class(
            data=filter_kwargs(), queryset=qs, request=info.context
        )
        if not filterset.form.is_valid():
            raise ValidationError(filterset.form.errors.as_json())
        return filterset.qs

    def get_queryset_resolver(self):
        return partial(
            self.resolve_queryset,
            filterset_class=self.filterset_class,
            filtering_args=self.filtering_args,
        )


class ConnectionField(RelayConnectionField):
    """Connection field."""

    def __init__(self, *args, **kwargs):
        self.enforce_first_or_last = kwargs.pop(
            "enforce_first_or_last",
            graphene_settings.RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST,
        )
        self.max_limit = kwargs.pop(
            "max_limit", graphene_settings.RELAY_CONNECTION_MAX_LIMIT
        )
        super().__init__(*args, **kwargs)

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection_type,
        enforce_first_or_last,
        max_limit,
        root,
        info,
        **kwargs,
    ):
        validate_first_and_last(info, enforce_first_or_last, max_limit, **kwargs)

        iterable = resolver(root, info, **kwargs)
        if iterable is None:
            iterable = []

        on_resolve = partial(cls.resolve_connection, connection_type, kwargs, iterable)

        if Promise.is_thenable(iterable):
            return Promise.resolve().then(on_resolve)
        return on_resolve()

    def wrap_resolve(self, parent_resolver):
        return partial(
            self.connection_resolver,
            parent_resolver,
            self.type,
            self.enforce_first_or_last,
            self.max_limit,
        )


class CursorConnectionField(ConnectionField):
    """Cursor connection field."""

    def __init__(self, *args, **kwargs):
        self.cursor_field = kwargs.pop("cursor_field", "id")
        super().__init__(*args, **kwargs)

    @classmethod
    def connection_resolver(
        cls,
        resolver,
        connection_type,
        enforce_first_or_last,
        max_limit,
        cursor_field,
        root,
        info,
        **kwargs,
    ):
        validate_first_and_last(info, enforce_first_or_last, max_limit, **kwargs)

        iterable = resolver(root, info, **kwargs)
        if iterable is None:
            iterable = []

        on_resolve = partial(
            cls.resolve_connection,
            connection_type,
            kwargs,
            iterable,
            max_limit,
            cursor_field,
        )

        if Promise.is_thenable(iterable):
            return Promise.resolve().then(on_resolve)
        return on_resolve()

    def wrap_resolve(self, parent_resolver):
        return partial(
            self.connection_resolver,
            parent_resolver,
            self.type,
            self.enforce_first_or_last,
            self.max_limit,
            self.cursor_field,
        )

    @classmethod
    def resolve_connection(cls, connection, args, iterable, max_limit, cursor_field):
        limit = min(args.get("first") or args.get("last"), max_limit)
        connection = connection_from_objects(
            iterable,
            limit,
            args,
            cursor_field,
            connection_type=partial(connection_adapter, connection),
            edge_type=connection.Edge,
            page_info_type=page_info_adapter,
        )
        connection.iterable = iterable
        connection.length = limit
        return connection


class DateTimeTZ(graphene.types.Scalar):
    """DateTime field with timezone support."""

    @staticmethod
    def serialize(value):
        if not value:
            return None
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone=tz.utc)
        return timezone.localtime(value).isoformat()

    @classmethod
    def parse_literal(cls, node):
        if not node.value:
            return None
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        value = graphene.DateTime.parse_value(value)
        if timezone.is_naive(value):
            value = timezone.make_aware(value, timezone=tz.utc)
        return timezone.localtime(value)


class File(graphene.types.Scalar):
    """File field."""

    @staticmethod
    def serialize(value):
        if not value:
            return ""
        return getattr(value, "url", "")

    @classmethod
    def parse_literal(cls, node):
        if not node.value:
            return None
        return cls.parse_value(node.value)

    @staticmethod
    def parse_value(value):
        return value


ModelCursorConnectionField = DjangoFilterCursorConnectionField
