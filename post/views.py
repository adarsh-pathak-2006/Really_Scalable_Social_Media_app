from django.shortcuts import render
from .models import Post, Reel
from authentication.models import Profile
from .serializer import PostSerializer, ReelSerializer
from rest_framework.generics import ListAPIView, ListCreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from social_media.pagination import GeneralReelAndPostPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

class PostFeedAPI(ListAPIView):
    serializer_class=PostSerializer
    queryset=Post.objects.select_related('user').all()
    pagination_class=GeneralReelAndPostPagination

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ReelFeedAPI(ListAPIView):
    serializer_class=ReelSerializer
    queryset=Reel.objects.select_related('user').all()
    pagination_class=GeneralReelAndPostPagination

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class MyPostAPI(ListCreateAPIView):
    serializer_class=PostSerializer
    queryset=Post.objects.select_related('user').all()
    pagination_class=GeneralReelAndPostPagination

    def perform_create(self, serializer):
        profile_data=Profile.objects.select_related('user').all()
        serializer.save(user=profile_data)

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)