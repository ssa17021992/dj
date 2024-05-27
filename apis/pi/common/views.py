from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from django.views.static import serve
from rest_framework import status

from apis.pi import generics, pagination
from apis.pi.common import serializers
from apis.pi.decorators import pi_throttle
from apps.common.utils import unique_id


class FruitAPIView(generics.ListAPIView):
    """Fruit api view"""

    serializer_list_class = serializers.ListFruitSerializer
    filter_backends = ()
    pagination_class = pagination.PageNumberPagination

    def get_queryset(self):
        search = self.request.query_params.get("search")
        fruits = cache.get("fruits")
        if not fruits:
            fruits = [
                {
                    "id": unique_id(11),
                    "name": f"Orange {x}",
                    "type": "citrus",
                    "created": timezone.now(),
                }
                for x in range(1, 1001)
            ]
            cache.set("fruits", fruits, None)
        if search:
            fruits = [fruit for fruit in fruits if fruit["name"].find(search) != -1]
        return fruits


class LocaltimeAPIView(generics.RetrieveAPIView):
    """Localtime api view"""

    serializer_list_class = serializers.LocaltimeSerializer

    def get_object(self):
        return {"localtime": timezone.now()}


class EchoAPIView(generics.CustomCreateAPIView):
    """Echo api view"""

    serializer_create_class = serializers.EchoSerializer
    status = status.HTTP_200_OK

    @pi_throttle(name="EchoAPIView.CREATE", limit=10, timeout=60)
    def post(self, *args, **kwargs):
        return super().post(*args, **kwargs)


class ServeAPIView(generics.APIView):
    """Serve api view"""

    def get(self, request, path, *args, **kwargs):
        return serve(request, path, document_root=settings.MEDIA_ROOT)


class SendEmailAPIView(generics.CustomCreateAPIView):
    """Send email api view"""

    serializer_create_class = serializers.SendEmailSerializer
    exclude_response_data = True
    status = status.HTTP_200_OK


class SendRoomMessageAPIView(generics.CustomCreateAPIView):
    """Send room message api view"""

    serializer_create_class = serializers.SendRoomMessageSerializer
    exclude_response_data = True
    status = status.HTTP_200_OK
