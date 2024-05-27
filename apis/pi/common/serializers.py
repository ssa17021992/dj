from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from rest_framework import serializers

from apis.pi import mixins
from apps.common.utils import exec_task, to_object


class EmptySerializer(serializers.Serializer):
    """Empty serializer"""

    def create(self, validated_data):
        return to_object({})

    def update(self, instance, validated_data):
        return instance


class ListFruitSerializer(mixins.QueryFieldsMixin, serializers.Serializer):
    """List fruit serializer"""

    id = serializers.CharField(max_length=22)
    name = serializers.CharField(max_length=50)
    type = serializers.CharField(max_length=10)
    created = serializers.DateTimeField()


class LocaltimeSerializer(serializers.Serializer):
    """Localtime serializer"""

    localtime = serializers.DateTimeField()


class EchoSerializer(serializers.Serializer):
    """Echo serializer"""

    message = serializers.CharField(max_length=150)

    def create(self, validated_data):
        return to_object(validated_data)


class SendEmailSerializer(serializers.Serializer):
    """Send email serializer"""

    subject = serializers.CharField(max_length=120)
    body = serializers.CharField(max_length=150)

    to = serializers.EmailField()

    def create(self, validated_data):
        exec_task("common.send_mail", kwargs=validated_data)
        return to_object(validated_data)


class SendRoomMessageSerializer(serializers.Serializer):
    """Send room message serializer"""

    content = serializers.CharField(max_length=250)

    def create(self, validated_data):
        room_name = "room_%(room_id)s" % self.context["view"].kwargs
        channel_layer = get_channel_layer()

        async_to_sync(channel_layer.group_send)(
            room_name,
            {
                "type": "room.message",
                "text_data": validated_data["content"],
                "user": None,
            },
        )
        return to_object(validated_data)
