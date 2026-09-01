from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES=[('MODERATOR', 'Moderator'), ('USER', 'User')]
    mobile_no=models.CharField(max_length=15, unique=True)
    role=models.CharField(max_length=10, choices=ROLE_CHOICES, default='USER')

class Profile(models.Model):
    user=models.OneToOneField(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=100)
    bio=models.TextField(null=True)
    profile_pic=models.ImageField(upload_to='pfps/', null=True)

    def __str__(self):
        return self.name

