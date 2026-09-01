from django.urls import path
from .views import PostFeedAPI, ReelFeedAPI, MyPostAPI, MyReelAPI

urlpatterns = [
    path('feed/posts/', PostFeedAPI.as_view(), name='post_feed'),
    path('feed/reels/', ReelFeedAPI.as_view(), name='reel_feed'),
    path('my/posts/', MyPostAPI.as_view(), name='my_posts'),
    path('my/reels/', MyReelAPI.as_view(), name='my_reels'),
]
