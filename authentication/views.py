from django.shortcuts import get_object_or_404
from .models import Profile
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import RegisterSerializer, ProfileSerializer
from django.db.models import Q
from django.db import transaction
from rest_framework.generics import RetrieveUpdateAPIView, ListAPIView
from social_media.pagination import GeneralReelAndPostPagination
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator


User=get_user_model()

class RegisterAPI(APIView):
    def post(self, request):
        serial=RegisterSerializer(data=request.data)
        if serial.is_valid():
            username=serial.validated_data['username']
            email=serial.validated_data['email']
            mobile_no=serial.validated_data['mobile_no']
            password=serial.validated_data['password']

            if User.objects.filter(Q(username=username) | Q(email=email) | Q(mobile_no=mobile_no)).exists():
                return Response({'message':'user with the credentials already exists'}, status=400)
            with transaction.atomic():
                user=User.objects.create_user(username=username, email=email, mobile_no=mobile_no, password=password)
                Profile.objects.create(user=user)
            return Response({'message':'user registered successfully'}, status=201)
        return Response(serial.errors, status=400)

class MyProfileAPI(RetrieveUpdateAPIView):
    serializer_class=ProfileSerializer

    def get_object(self):
        return get_object_or_404(Profile.objects.select_related('user'), user=self.request.user)

class AllProfileAPI(ListAPIView):
    serializer_class=ProfileSerializer
    queryset=Profile.objects.select_related('user').all()
    pagination_class=GeneralReelAndPostPagination

    @method_decorator(cache_page(60 * 5))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)