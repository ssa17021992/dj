from django.urls import path, register_converter

from apis.ws.common import consumers
from apps.common import converters

register_converter(converters.B64Converter, "b64")

urlpatterns = [
    path("rooms/<b64:room_id>", consumers.ChatConsumer.as_asgi(), name="chat"),
    path("echo", consumers.EchoConsumer.as_asgi(), name="echo"),
]
