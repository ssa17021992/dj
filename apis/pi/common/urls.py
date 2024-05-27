from django.urls import path, register_converter

from apis.pi.common import views
from apps.common import converters

register_converter(converters.B64Converter, "b64")

urlpatterns = [
    path("fruits", views.FruitAPIView.as_view(), name="fruit"),
    path("localtime", views.LocaltimeAPIView.as_view(), name="localtime"),
    path("echo", views.EchoAPIView.as_view(), name="echo"),
    path("serve/<path:path>", views.ServeAPIView.as_view(), name="serve"),
    path("send-email", views.SendEmailAPIView.as_view(), name="send_email"),
    path(
        "rooms/<b64:room_id>/send-message",
        views.SendRoomMessageAPIView.as_view(),
        name="room_send_message",
    ),
]
