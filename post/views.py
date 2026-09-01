from django.shortcuts import get_object_or_404
from .models import Post, Reel
from authentication.models import Profile
from .serializer import PostSerializer, ReelSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from social_media.pagination import GeneralReelAndPostPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from .cache_key import post_cache_key, reel_cache_key
from django.core.cache import cache

class PostFeedAPI(ListAPIView):
    serializer_class=PostSerializer
    queryset=Post.objects.select_related('user').all().filter('-created_on')
    pagination_class=GeneralReelAndPostPagination

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class ReelFeedAPI(ListAPIView):
    serializer_class=ReelSerializer
    queryset=Reel.objects.select_related('user').all().filter('-created_on')
    pagination_class=GeneralReelAndPostPagination

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class MyPostAPI(APIView):
    def get(self, request):
        page_no=request.query_params.get("page", "1")
        key=post_cache_key(page=page_no, user_id=request.user.id)
        cached_data=cache.get(key=key)
        if cached_data is not None:
            return Response(cached_data, status=200)
        paginator=GeneralReelAndPostPagination()
        queryset=paginator.paginate_queryset(Post.objects.select_related('user__user').filter(user__user=request.user).order_by('-created_on'), request, view=self)
        serial=PostSerializer(queryset, many=True)
        response=paginator.get_paginated_response(serial.data)
        cache.set(key, response.data, timeout=300)
        return response

    def post(self, request):
        serial=PostSerializer(data=request.data)
        if serial.is_valid():
            profile_data=get_object_or_404(Profile.objects.select_related('user'), user=request.user)
            serial.save(user=profile_data)
            for i in range(1,21):
                key=post_cache_key(page=i, user_id=request.user.id)
                cache.delete(key)
            return Response(serial.data, status=201)
        return Response(serial.errors, status=400)

class MyReelAPI(APIView):
    def get(self, request):
        page_no=request.query_params.get("page","1")
        key=reel_cache_key(page=page_no, user_id=request.user.id)
        cached_data=cache.get(key)
        if cached_data:
            return Response(cached_data, status=200)
        paginator=GeneralReelAndPostPagination()
        queryset=paginator.paginate_queryset(Reel.objects.select_related('user__user').filter(user__user=request.user).order_by('-created_on'), request, view=self)
        serial=ReelSerializer(queryset, many=True)
        response=paginator.get_paginated_response(serial.data)
        cache.set(key, response.data, timeout=300)
        return response

    def post(self, request):
        serial=ReelSerializer(data=request.data)
        if serial.is_valid():
            profile_data=Profile.objects.select_related('user').get(user=request.user)
            serial.save(user=profile_data)
            for i in range(1, 21):
                key=reel_cache_key(i, request.user.id)
                cache.delete(key=key)
            return Response(serial.data, status=201)
        return Response(serial.errors, status=400)