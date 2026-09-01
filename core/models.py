from django.db import models
from authentication.models import Profile

class Follower(models.Model):
    user=models.ForeignKey(Profile, on_delete=models.CASCADE)
    follower=models.ManyToManyField(Profile, related_name='follower_of')
    created_on=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.name
