from django.urls import path

from apis.ws.accounts import consumers

urlpatterns = [
    path("notes", consumers.NoteConsumer.as_asgi(), name="notes"),
]
