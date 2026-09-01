from django.db import models
from authentication.models import Profile

class Post(models.Model):
    user=models.ForeignKey(Profile, on_delete=models.CASCADE)
    title=models.CharField(max_length=200, null=True)
    content=models.TextField(null=True)
    image=models.ImageField(upload_to='posts/')
    created_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:80]

class Reel(models.Model):
    user=models.ForeignKey(Profile, on_delete=models.CASCADE)
    title=models.CharField(max_length=200, null=True)
    description=models.TextField(null=True)
    media=models.FileField(upload_to='reels/')
    created_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title[:80]
