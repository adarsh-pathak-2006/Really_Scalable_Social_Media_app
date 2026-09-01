from django.db import models
from authentication.models import Profile

class Follower(models.Model):
    follower=models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='following_relationship')
    following=models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='follower_of')
    created_on=models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints=[models.UniqueConstraint(fields=['follower', 'following'], name='unique_follower_following')]

    def __str__(self):
        return self.user.name
