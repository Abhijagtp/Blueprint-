# Users/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import ActivityLog 

from WorkListing.models import ProjectRequest
from Users.models import CustomUser, UserProfile,Post, Like, Comment,FollowRequest, Message, GroupMessage
from Training.models import Enrollment
from Dashboard.models import Email
from django.contrib.contenttypes.models import ContentType

# Existing signals (unchanged)
@receiver(post_save, sender=FollowRequest)
def log_follow_request_activity(sender, instance, created, **kwargs):
    if created and instance.status == 'pending':
        ActivityLog.objects.create(
            user=instance.to_user,
            actor=instance.from_user,
            activity_type='follow_request',
            content=f"{instance.from_user.get_full_name()} sent you a follow request.",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=Message)
def log_message_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.receiver,
            actor=instance.sender,
            activity_type='message',
            content=f"{instance.sender.get_full_name()} sent you a message: {instance.content[:50]}...",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=GroupMessage)
def log_group_message_activity(sender, instance, created, **kwargs):
    if created:
        group_members = instance.group.members.exclude(id=instance.sender.id)
        for member in group_members:
            ActivityLog.objects.create(
                user=member,
                actor=instance.sender,
                activity_type='group_message',
                content=f"{instance.sender.get_full_name()} sent a message in {instance.group.name}: {instance.content[:50]}...",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=Enrollment)
def log_enrollment_activity(sender, instance, created, **kwargs):
    if created:
        ActivityLog.objects.create(
            user=instance.course.instructor,
            actor=instance.user,
            activity_type='enrollment',
            content=f"{instance.user.get_full_name()} enrolled in your course: {instance.course.title}.",
            content_type=ContentType.objects.get_for_model(instance),
            object_id=instance.id
        )

@receiver(post_save, sender=Email)
def log_email_activity(sender, instance, created, **kwargs):
    if created:
        for recipient in instance.recipients.all():
            ActivityLog.objects.create(
                user=recipient,
                actor=instance.sender,
                activity_type='email',
                content=f"{instance.sender.get_full_name()} sent you an email: {instance.subject}.",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

# New signals for likes, comments, follower posts, and project request status changes
@receiver(post_save, sender=Like)
def log_like_activity(sender, instance, created, **kwargs):
    if created:
        post_owner = instance.post.user_profile.user
        if instance.user_profile.user != post_owner:  # Don't notify if the user likes their own post
            ActivityLog.objects.create(
                user=post_owner,
                actor=instance.user_profile.user,
                activity_type='like',
                content=f"{instance.user_profile.user.get_full_name()} liked your post.",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=Comment)
def log_comment_activity(sender, instance, created, **kwargs):
    if created:
        post_owner = instance.post.user_profile.user
        if instance.user_profile.user != post_owner:  # Don't notify if the user comments on their own post
            ActivityLog.objects.create(
                user=post_owner,
                actor=instance.user_profile.user,
                activity_type='comment',
                content=f"{instance.user_profile.user.get_full_name()} commented on your post: {instance.text[:50]}...",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

@receiver(post_save, sender=Post)
def log_follower_post_activity(sender, instance, created, **kwargs):
    if created:
        # Get the followers of the post creator
        creator = instance.user_profile.user
        # Find followers by looking at accepted FollowRequests
        followers = CustomUser.objects.filter(
            sent_requests__to_user=creator,
            sent_requests__status='accepted'
        )
        for follower in followers:
            # Safely handle caption or fallback to content_type
            content_preview = (
                instance.caption[:50] if instance.caption else str(instance.content_type)
            )
            ActivityLog.objects.create(
                user=follower,
                actor=creator,
                activity_type='follower_post',
                content=f"{creator.get_full_name()} created a new post: {content_preview}...",
                content_type=ContentType.objects.get_for_model(instance),
                object_id=instance.id
            )

# Signal to track project request status changes
@receiver(pre_save, sender=ProjectRequest)
def log_project_request_status_change(sender, instance, **kwargs):
    if instance.id:  # Only trigger if the project request already exists (i.e., it's being updated)
        try:
            old_instance = ProjectRequest.objects.get(id=instance.id)
            if old_instance.status != instance.status:  # Status has changed
                if instance.status == 'accepted':
                    ActivityLog.objects.create(
                        user=instance.professional,
                        actor=instance.project.org,  # The organization is the actor
                        activity_type='project_request_accepted',
                        content=f"Your request for the project '{instance.project.domain}' has been accepted by {instance.project.org.get_full_name()}.",
                        content_type=ContentType.objects.get_for_model(instance),
                        object_id=instance.id
                    )
                elif instance.status == 'rejected':
                    ActivityLog.objects.create(
                        user=instance.professional,
                        actor=instance.project.org,  # The organization is the actor
                        activity_type='project_request_rejected',
                        content=f"Your request for the project '{instance.project.domain}' has been rejected by {instance.project.org.get_full_name()}.",
                        content_type=ContentType.objects.get_for_model(instance),
                        object_id=instance.id
                    )
        except ProjectRequest.DoesNotExist:
            pass  # Project request is being created, not updated