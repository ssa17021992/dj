from rest_framework import generics, serializers, status, views
from rest_framework.response import Response

from apis.auth import TokenAuth
from apis.pi import mixins

"""
Generic views that provide commonly needed behaviour.
"""


class APIView(views.APIView):
    """Api view."""

    def get_authenticate_header(self, request):
        """
        If a request is unauthenticated, determine the WWW-Authenticate
        header to use for 401 responses, if any.
        """
        return TokenAuth.keyword


class GenericAPIView(APIView, generics.GenericAPIView):
    """Base class for all other generic views."""

    serializer_create_class = None
    serializer_list_class = None
    serializer_update_class = None
    actions = {
        "POST": "create",
        "GET": "list",
        "PUT": "update",
        "PATCH": "update",
        "DELETE": "delete",
    }

    def get_request_data(self):
        """Return the request data."""
        return self.request.data

    def get_response_data(self, serializer):
        """Return the response data."""
        if self.request.method == "GET":
            return serializer.data
        if self.serializer_list_class is not None:
            serializer = self.serializer_list_class(
                serializer.instance, context=serializer.context
            )
        return serializer.data

    def get_serializer(self, *args, **kwargs):
        """Return the serializer instance."""
        action = self.actions.get(self.request.method)
        serializer_class = getattr(self, "serializer_%s_class" % action, None)
        kwargs["context"] = self.get_serializer_context()
        return (serializer_class or serializers.Serializer)(*args, **kwargs)


# Concrete view classes that provide method handlers
# by composing the mixin classes with the base view.


class CreateAPIView(mixins.CreateModelMixin, GenericAPIView):
    """Concrete view for creating a model instance."""

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ListAPIView(mixins.ListModelMixin, GenericAPIView):
    """Concrete view for listing a queryset."""

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class RetrieveAPIView(mixins.RetrieveModelMixin, GenericAPIView):
    """Concrete view for retrieving a model instance."""

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)


class UpdateAPIView(mixins.UpdateModelMixin, GenericAPIView):
    """Concrete view for updating a model instance."""

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class DestroyAPIView(mixins.DestroyModelMixin, GenericAPIView):
    """Concrete view for deleting a model instance."""

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ListCreateAPIView(mixins.ListModelMixin, mixins.CreateModelMixin, GenericAPIView):
    """Concrete view for listing a queryset or creating a model instance."""

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RetrieveUpdateAPIView(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, GenericAPIView
):
    """Concrete view for retrieving, updating a model instance."""

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class RetrieveDestroyAPIView(
    mixins.RetrieveModelMixin, mixins.DestroyModelMixin, GenericAPIView
):
    """Concrete view for retrieving or deleting a model instance."""

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class RetrieveUpdateDestroyAPIView(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    GenericAPIView,
):
    """Concrete view for retrieving, updating or deleting a model instance."""

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CustomCreateAPIView(GenericAPIView):
    """Custom create api view."""

    as_update = False
    exclude_response_data = False
    status = status.HTTP_201_CREATED

    def create(self, request, *args, **kwargs):
        data = self.get_request_data()

        if self.as_update:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=data)
        else:
            serializer = self.get_serializer(data=data)

        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        if self.exclude_response_data:
            return Response(status=self.status)

        data = self.get_response_data(serializer)
        return Response(data, status=self.status)

    def perform_create(self, serializer):
        serializer.save()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
