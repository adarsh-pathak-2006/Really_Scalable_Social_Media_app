import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import ChatRoom, Message
from authentication.models import Profile

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        if self.user.is_anonymous or self.user.role not in ['MODERATOR', 'USER']:
            await self.close()
            return

        self.room = await self.get_room(self.room_name)
        if not self.room:
            await self.close()
            return

        is_participant = await self.check_participant(self.room, self.user)
        if not is_participant:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'room_group_name'):
            # Leave room group
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')
        if not message:
            return

        # Save message to database
        saved_msg = await self.save_message(self.room, self.user, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender_name': saved_msg.sender.name,
                'timestamp': str(saved_msg.timestamp),
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        sender_name = event['sender_name']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender_name': sender_name,
            'timestamp': timestamp,
        }))

    @database_sync_to_async
    def get_room(self, room_id):
        try:
            return ChatRoom.objects.get(id=room_id)
        except (ChatRoom.DoesNotExist, ValueError):
            return None

    @database_sync_to_async
    def check_participant(self, room, user):
        try:
            profile = Profile.objects.get(user=user)
            return room.participants.filter(id=profile.id).exists()
        except Profile.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, room, user, content):
        profile = Profile.objects.get(user=user)
        msg = Message.objects.create(room=room, sender=profile, content=content)
        return msg
