from rest_framework.serializers import ModelSerializer
from .models import Post, Reel
from authentication.serializers import ProfileGetSerializer

class PostSerializer(ModelSerializer):
    user=ProfileGetSerializer(read_only=True)
    class Meta:
        model=Post
        fields='__all__'
        read_only_fields=['created_on']

class ReelSerializer(ModelSerializer):
    user=ProfileGetSerializer(read_only=True)
    class Meta:
        model=Reel
        fields='__all__'
        read_only_fields=['created_on']