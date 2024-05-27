from apis.ws.auth import auth_required
from apis.ws.common import consumers
from apis.ws.common.utils import db_async, ws_data


class NoteConsumer(consumers.WebSocketConsumer):
    """Note consumer."""

    @auth_required
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data=None, bytes_data=None):
        create_note = db_async(self.ctx.user.notes.create)
        note = await create_note(content=text_data or "")
        data = {
            "id": note.pk,
            "content": note.content,
            "created": note.created.isoformat(),
        }
        await self.send(text_data=ws_data(action="note", data=data))
