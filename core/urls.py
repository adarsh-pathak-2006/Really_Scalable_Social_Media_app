from django.urls import path
from .views import FollowAPI

urlpatterns = [
    path('follow/<int:pk>/', FollowAPI.as_view(), name='follow_user'),
]
