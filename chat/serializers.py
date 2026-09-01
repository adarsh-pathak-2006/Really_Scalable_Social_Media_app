from rest_framework import serializers
from .models import ChatRoom, Message
from authentication.serializers import ProfileGetSerializer

class MessageSerializer(serializers.ModelSerializer):
    sender = ProfileGetSerializer(read_only=True)
    class Meta:
        model = Message
        fields = ['id', 'room', 'sender', 'content', 'timestamp', 'is_read']

class ChatRoomSerializer(serializers.ModelSerializer):
    participants = ProfileGetSerializer(many=True, read_only=True)
    latest_message = serializers.SerializerMethodField()

    class Meta:
        model = ChatRoom
        fields = ['id', 'participants', 'created_at', 'latest_message']

    def get_latest_message(self, obj):
        msg = obj.messages.order_by('-timestamp').first()
        if msg:
            return MessageSerializer(msg).data
        return None
