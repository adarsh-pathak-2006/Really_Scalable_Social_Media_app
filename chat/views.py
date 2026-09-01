from rest_framework import generics
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer
from authentication.models import Profile
from social_media.pagination import GeneralReelAndPostPagination

class RoomListAPI(generics.ListAPIView):
    serializer_class = ChatRoomSerializer
    pagination_class = GeneralReelAndPostPagination
    
    def get_queryset(self):
        try:
            profile = Profile.objects.get(user=self.request.user)
            return profile.chat_rooms.all().order_by('-created_at')
        except Profile.DoesNotExist:
            return ChatRoom.objects.none()

class MessageHistoryAPI(generics.ListAPIView):
    serializer_class = MessageSerializer
    pagination_class = GeneralReelAndPostPagination
    
    def get_queryset(self):
        room_id = self.kwargs['room_id']
        try:
            profile = Profile.objects.get(user=self.request.user)
            room = ChatRoom.objects.get(id=room_id, participants=profile)
            return room.messages.all().order_by('-timestamp')
        except (Profile.DoesNotExist, ChatRoom.DoesNotExist):
            return Message.objects.none()
