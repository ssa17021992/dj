from rest_framework import status
from rest_framework.response import Response

"""
Basic building blocks for generic class based views.
"""


class CreateModelMixin:
    """Create a model instance."""

    def create(self, request, *args, **kwargs):
        data = self.get_request_data()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = self.get_response_data(serializer)
        return Response(data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()


class ListModelMixin:
    """List a queryset."""

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.get_response_data(serializer)
            return self.get_paginated_response(data)

        serializer = self.get_serializer(queryset, many=True)
        data = self.get_response_data(serializer)
        return Response(data)


class RetrieveModelMixin:
    """Retrieve a model instance."""

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = self.get_response_data(serializer)
        return Response(data)


class UpdateModelMixin:
    """Update a model instance."""

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = self.get_request_data()
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response()

    def partial_update(self, request, *args, **kwargs):
        kwargs["partial"] = True
        return self.update(request, *args, **kwargs)

    def perform_update(self, serializer):
        serializer.save()


class DestroyModelMixin:
    """Destroy a model instance."""

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class QueryFieldsMixin:
    """Query fields mixin."""

    include_arg_name = "fields"
    exclude_arg_name = "fields!"
    delimiter = ","

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        request = self.context.get("request")
        if not hasattr(request, "query_params"):
            return None

        query_params = request.query_params

        includes = query_params.getlist(self.include_arg_name)
        include_field_names = {
            name for names in includes for name in names.split(self.delimiter) if name
        }

        excludes = query_params.getlist(self.exclude_arg_name)
        exclude_field_names = {
            name for names in excludes for name in names.split(self.delimiter) if name
        }

        if not include_field_names and not exclude_field_names:
            return None

        serializer_field_names = set(self.fields)
        fields_to_drop = serializer_field_names & exclude_field_names

        if include_field_names:
            fields_to_drop |= serializer_field_names - include_field_names

        for field in fields_to_drop:
            self.fields.pop(field)


class RequestUserMixin:
    """Return self.request.user in get_object method."""

    def get_object(self):
        return self.request.user
