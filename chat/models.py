from django.db import models
from authentication.models import Profile

class ChatRoom(models.Model):
    participants = models.ManyToManyField(Profile, related_name='chat_rooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ChatRoom {self.id}"

class Message(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='messages_sent')
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Message by {self.sender.name} at {self.timestamp}"
