from django.db import models
from django.contrib.auth import get_user_model
import uuid
from datetime import datetime

User = get_user_model()

# Create your models here
class Profile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_user = models.IntegerField()
    bio = models.TextField(blank=True)
    profile_img = models.ImageField(upload_to='profile_images', default='blank-profile-picture.png')

    def __str__(self):
        return self.user.username

class Post(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.CharField(max_length=100)
    image = models.ImageField(upload_to='post_images')
    caption = models.TextField()
    created_at = models.DateTimeField(default=datetime.now)
    no_of_likes = models.IntegerField(default=0)

    def __str__(self):
        return self.user

class LikePost(models.Model):
    post_id = models.CharField(max_length=500)
    user = models.CharField(max_length=500)

    def __str__(self):
        return self.user

class FollowersCount(models.Model):
    follower = models.CharField(max_length=100)
    user = models.CharField(max_length=100)

    def __str__(self):
        return self.user

class Comment(models.Model):
    post_id = models.CharField(max_length=500)
    user_id = models.CharField(max_length=500)
    comment = models.TextField()
    comment_date = models.DateTimeField(default=datetime.now)

class Category(models.Model):
    category_id = models.CharField(max_length=500)
    category_name = models.CharField(max_length=100)

class CategoryPost(models.Model):
    category_id = models.CharField(max_length=500)
    post_id = models.CharField(max_length=500)