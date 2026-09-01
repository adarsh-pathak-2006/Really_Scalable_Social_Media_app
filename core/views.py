from django.shortcuts import render
from .models import Follow
from authentication.models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response

class FollowAPI(APIView):
    def post(self, request, pk):
        
