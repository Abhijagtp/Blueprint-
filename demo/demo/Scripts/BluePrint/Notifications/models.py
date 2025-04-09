from django.db import models

# Create your models here.
# Users/models.py
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class ActivityLog(models.Model):
    ACTIVITY_TYPES = [
        ('follow_request', 'Follow Request'),
        ('message', 'Message'),
        ('group_message', 'Group Message'),
        ('enrollment', 'Course Enrollment'),
        ('email', 'Email'),
        ('like', 'Like'),  # For likes on posts
        ('comment', 'Comment'),  # For comments on posts
        ('follower_post', 'Follower Post'),  # For posts by followed users
        ('project_request_accepted', 'Project Request Accepted'),  # For project request acceptance
        ('project_request_rejected', 'Project Request Rejected'),  # For project request rejection
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='activity_logs')  # The user who receives the notification
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='performed_activities')  # The user who performed the action
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    content = models.TextField(blank=True, null=True)  # A brief description of the action
    timestamp = models.DateTimeField(auto_now_add=True)
    seen = models.BooleanField(default=False)

    # Generic foreign key to reference any model
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return f"{self.actor.get_full_name()} {self.get_activity_type_display()} for {self.user.get_full_name()} at {self.timestamp}"