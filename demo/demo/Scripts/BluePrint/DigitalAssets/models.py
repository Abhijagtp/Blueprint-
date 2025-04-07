from django.db import models

# Create your models here.


from Users.models import CustomUser,UserProfile,Post

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


# blog

class Blog(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="blogs")
    title = models.CharField(max_length=255)
    content = models.TextField()
    language = models.CharField(max_length=10, default="en")
    categories = models.JSONField(default=list)
    thumbnail = models.ImageField(upload_to='blog_thumbnails/', blank=True, null=True)
    media_files = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    is_draft = models.BooleanField(default=True)  # New field, defaults to True

    def __str__(self):
        return self.title



# whitePaper 

class Whitepaper(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE,related_name="whitepapers")
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)
    content = models.TextField(blank=True)
    sources = models.JSONField(default=list)  # Store as JSON list
    categories = models.JSONField(default=list)  # Store as JSON list
    is_draft = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True) # New field, defaults to True

    def __str__(self):
        return self.title




# insights 
class Insight(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="insights")
    title = models.CharField(max_length=255)
    content = models.TextField()
    summary = models.TextField(blank=True, null=True)
    sources = models.JSONField(default=list)
    language = models.CharField(max_length=10, default="en")
    categories = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)
    is_draft = models.BooleanField(default=True)  # New field, defaults to True

    def __str__(self):
        return self.title

