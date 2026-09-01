from rest_framework.serializers import ModelSerializer
from .models import Profile
from django.contrib.auth import get_user_model


User=get_user_model()

class UserGetSerializer(ModelSerializer):
    class Meta:
        model=User
        fields=['username', 'role']

class RegisterSerializer(ModelSerializer):
    class Meta:
        model=User
        fields=['username', 'email', 'mobile_no', 'password']

class ProfileSerializer(ModelSerializer):
    user=UserGetSerializer(read_only=True)
    class Meta:
        model=Profile
        fields='__all__'

class ProfileGetSerializer(ModelSerializer):
    user=UserGetSerializer(read_only=True)
    class Meta:
        model=Profile
        fields=['user', 'name']
