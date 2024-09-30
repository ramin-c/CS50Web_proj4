from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Follower_list(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following", unique=True)
    follows_user = models.ManyToManyField(User, blank=True, related_name="followed_user")


class Post(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    content = models.CharField(max_length=50000)


class Like(models.Model):
    liked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    post_liked = models.ForeignKey(Post, on_delete=models.CASCADE)