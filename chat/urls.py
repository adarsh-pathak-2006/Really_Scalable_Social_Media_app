from django.urls import path
from .views import RoomListAPI, MessageHistoryAPI

urlpatterns = [
    path('rooms/', RoomListAPI.as_view(), name='room_list'),
    path('rooms/<int:room_id>/messages/', MessageHistoryAPI.as_view(), name='message_history'),
]
