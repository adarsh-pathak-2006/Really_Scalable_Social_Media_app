from django.shortcuts import get_object_or_404
from .models import Follow
from authentication.models import Profile
from rest_framework.views import APIView
from rest_framework.response import Response
from social_media.permissions import IsCustomer

class FollowAPI(APIView):
    permission_classes=[IsCustomer]
    def post(self, request, pk):
        myprofile_data=get_object_or_404(Profile.objects.select_related('user'), user=request.user)
        personprofile_data=get_object_or_404(Profile, id=pk)
        Follow.objects.create(follower=myprofile_data, following=personprofile_data)
        return Response({'message':'followed the user'})
