from django.shortcuts import get_object_or_404
from .models import Post, Reel
from authentication.models import Profile
from .serializer import PostSerializer, ReelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, ListCreateAPIView
from social_media.pagination import GeneralReelAndPostPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.core.cache import cache

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

# class MyPostAPI(ListCreateAPIView):
#     serializer_class=PostSerializer
#     pagination_class=GeneralReelAndPostPagination

#     def get_queryset(self):
#         return Post.objects.select_related('user').filter(user=self.request.user)

#     def perform_create(self, serializer):
#         profile_data=get_object_or_404(Profile.objects.select_related('user'), user=self.request.user)
#         serializer.save(user=profile_data)

class MyPostAPI(APIView):
    def get(self, request):
        paginator=GeneralReelAndPostPagination()
        queryset=paginator.paginate_queryset(Post.objects.select_related('user__user').filter(user__user=request.user).order_by('-created_on'), request, view=self)
        serial=PostSerializer(queryset, many=True)
        return paginator.get_paginated_response(serial.data)

    def post(self, request):
        serial=PostSerializer(data=request.data)
        if serial.is_valid():
            profile_data=get_object_or_404(Profile.objects.select_related('user'), user=request.user)
            serial.save(user=profile_data)
            return Response(serial.data, status=201)
        return Response(serial.errors, status=400)


class MyReelAPI(ListCreateAPIView):
    serializer_class=ReelSerializer
    pagination_class=GeneralReelAndPostPagination

    def get_queryset(self):
        return Reel.objects.select_related('user__user').filter(user__user=self.request.user).order_by('-created_on')

    def perform_create(self, serializer):
        profile_data=get_object_or_404(Profile.objects.select_related('user'), user=self.request.user)
        serializer.save(user=profile_data)
