from channels.generic.websocket import AsyncWebsocketConsumer as WebSocketConsumer

from apis.ws.auth import ctx
from apis.ws.common.utils import ws_data


class NotFoundConsumer(WebSocketConsumer):
    """Not found consumer."""

    async def connect(self):
        await self.close()


class ChatConsumer(WebSocketConsumer):
    """Chat consumer."""

    @property
    def room_name(self):
        return "room_%(room_id)s" % self.scope["url_route"]["kwargs"]

    @ctx
    async def connect(self):
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "room.message",
                "text_data": text_data,
            },
        )

    async def room_message(self, event):
        data = {
            "user": str(self.ctx.user),
            "message": event.get("text_data"),
        }
        await self.send(text_data=ws_data(action="room", data=data))


class EchoConsumer(WebSocketConsumer):
    """Echo consumer."""

    @ctx
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        data = {
            "user": str(self.ctx.user),
            "message": text_data,
        }
        await self.send(text_data=ws_data(action="echo", data=data))
