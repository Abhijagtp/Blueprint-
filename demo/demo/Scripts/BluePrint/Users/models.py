from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    PROFESSIONAL = 'professional'
    ORGANIZATIONAL = 'organizational'
    INSTRUCTOR = 'instructor'
    INSTITUTIONAL = 'institutional'

    USER_TYPE_CHOICES = [
        (PROFESSIONAL, 'Professional'),
        (ORGANIZATIONAL, 'Organizational'),
        (INSTRUCTOR, 'Instructor'),
        (INSTITUTIONAL, 'Institutional'),
    ]
    
    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default=PROFESSIONAL,
    )

    full_name = models.CharField(max_length=255, blank=True, null=True)  # Add this field

    def __str__(self):
        return self.full_name if self.full_name else self.username



from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    bio = models.TextField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    profile_image = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    cover_image = models.ImageField(upload_to='cover_images/', blank=True, null=True)

class Experience(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="experiences")
    title = models.CharField(max_length=255)
    organization_name = models.CharField(max_length=255)
    is_current = models.BooleanField(default=False)
    from_date = models.DateField(null=True, blank=True)
    to_date = models.DateField(null=True, blank=True)
    skills_gained = models.TextField(blank=True, null=True)

class Education(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="educations")
    institute_name = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    is_studying = models.BooleanField(default=False)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

class Skill(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="skills")
    skill_name = models.CharField(max_length=100)


from django.db import models
from django.contrib.auth.models import User

class Certification(models.Model):
    user_profile = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="certifications")
    course_name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255)
    completion_date = models.DateField()
    skills_gained = models.ManyToManyField(Skill, related_name="certifications")
    certificate_file = models.FileField(upload_to="certificates/", blank=True, null=True)

    def __str__(self):
        return f"{self.course_name} - {self.issuing_organization}"



from django.db import models

class Project(models.Model):
    user_profile = models.ForeignKey("UserProfile", on_delete=models.CASCADE, related_name="projects")
    title = models.CharField(max_length=255)
    description = models.TextField()
    technologies = models.CharField(max_length=255)  # Store as comma-separated values
    image1 = models.ImageField(upload_to='projects/', blank=True, null=True)
    image2 = models.ImageField(upload_to='projects/', blank=True, null=True)

    def get_technologies_list(self):
        return self.technologies.split(',')
    

# POST 
from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="posts")
    caption = models.TextField(blank=True, null=True)  # For normal posts
    image = models.ImageField(upload_to='post_images/', blank=True, null=True)  # For normal posts
    content_type = models.CharField(max_length=20, choices=[
        ('normal', 'Normal Post'),
        ('blog', 'Blog'),
        ('whitepaper', 'Whitepaper'),
        ('insight', 'Insight'),
    ])
    content_id = models.PositiveIntegerField(blank=True, null=True)  # ID of the specific content
    created_at = models.DateTimeField(auto_now_add=True)
    saved_by = models.ManyToManyField(UserProfile, related_name='saved_posts', blank=True)

    class Meta:
        unique_together = ('user_profile', 'content_type', 'content_id')  # Ensure uniqueness

    def __str__(self):
        return self.caption[:50] if self.caption else f"{self.content_type} post"
    

class Like(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user_profile', 'post')  # Ensures a user can like a post only once

    def __str__(self):
        return f"{self.user.username} liked {self.post.title}"


class Comment(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    text = models.TextField()
    # Self-referential foreign key for replies:
    parent = models.ForeignKey('self', null=True, blank=True, related_name='replies', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment by {self.user_profile.user.get_full_name()} on {self.post.caption[:20]}"



from django.db import models
from django.contrib.auth.models import User

class FollowRequest(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined'),
    )
    
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='received_requests')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.from_user.get_full_name()} -> {self.to_user.get_full_name()} [{self.status}]"



from django.db import models
from django.conf import settings

from django.utils.timezone import localtime

from django.utils.timezone import localtime
from datetime import datetime

class Message(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="sent_messages")
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="received_messages")
    content = models.TextField()
    timestamp = models.DateTimeField()  # Remove auto_now_add=True
    is_read = models.BooleanField(default=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, blank=True, null=True)  # Shared post

    class Meta:
        ordering = ['-timestamp']

    def is_post_share(self):
        return self.post is not None
    
    def save(self, *args, **kwargs):
        """Ensure timestamp is saved in local time."""
        if not self.timestamp:
            self.timestamp = datetime.now()  # Save in system local time
        super().save(*args, **kwargs)




from django.db import models
from django.contrib.auth import get_user_model



class ChatGroup(models.Model):
    name = models.CharField(max_length=255)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="created_groups")
    members = models.ManyToManyField(CustomUser, related_name="chat_groups")
    group_picture = models.ImageField(upload_to="group_pictures/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.name


class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.content[:50]}"




# models for FORM - 

# org form model 


from django.db import models

class Organization(models.Model):
    INDUSTRY_CHOICES = [
        ('IT', 'Information Technology'),
        ('FIN', 'Finance'),
        ('EDU', 'Education'),
        ('HLTH', 'Healthcare'),
        ('MFG', 'Manufacturing'),
    ]
    BUSINESS_TYPE_CHOICES = [
        ('B2B', 'Business-to-Business'),
        ('B2C', 'Business-to-Consumer'),
        ('B2G', 'Business-to-Government'),
    ]
    NATURE_CHOICES = [
        ('PROD', 'Product-based'),
        ('SERV', 'Service-based'),
        ('HYBRID', 'Hybrid'),
        ('PROFESSIONAL', 'Professional'),  # Fixed tuple syntax
    ]
    EDUCATION_CHOICES = [
        ('BACHELOR', 'Bachelor'),
        ('MASTER', 'Master'),
        ('PHD', 'Ph.D'),
    ]
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization'
    )
    industry_type = models.CharField(max_length=100, choices=INDUSTRY_CHOICES)
    organization_name = models.CharField(max_length=200)
    total_employees = models.IntegerField()
    description = models.TextField()
    revenue = models.DecimalField(max_digits=15, decimal_places=2)
    gst_number = models.CharField(max_length=15)
    start_year = models.IntegerField()
    business_type = models.CharField(max_length=100, choices=BUSINESS_TYPE_CHOICES)
    business_nature = models.CharField(max_length=100, choices=NATURE_CHOICES)
    challenges = models.TextField()
    digital_assets = models.TextField()
    desired_assets = models.TextField()
    skills = models.TextField()  # Comma-separated skills
    wish_to_expand = models.BooleanField()
    locations = models.TextField()  # Comma-separated locations
    education = models.CharField(max_length=50, choices=EDUCATION_CHOICES)
    website_link = models.URLField()
    open_positions = models.TextField()  # Comma-separated positions
    willing_to_collaborate = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.organization_name



# user form 

# models.py
from django.db import models

class Degree(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class Specialization(models.Model):
    degree = models.ForeignKey(Degree, on_delete=models.CASCADE, related_name='specializations')
    name = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.name} ({self.degree.name})"

class Industry(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name

class User_form(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='Professional'
    )
    # Educational Information
    highest_degree = models.ForeignKey(Degree, on_delete=models.SET_NULL, null=True)
    specialization = models.ForeignKey(Specialization, on_delete=models.SET_NULL, null=True)
    graduation_year = models.IntegerField()
    years_of_experience = models.IntegerField()
    
    # Details
    current_occupation = models.CharField(max_length=100)
    current_organization = models.CharField(max_length=200)
    top_skills = models.JSONField(default=list)  # For storing list of skills
    is_fresher = models.BooleanField(default=False)
    on_career_break = models.BooleanField(default=False)
    
    # Career Goal
    preferred_industry = models.ForeignKey(Industry, on_delete=models.SET_NULL, null=True)
    desired_job_role = models.CharField(max_length=100)
    specific_position = models.CharField(max_length=100)
    career_goal_skills = models.JSONField(default=list)
    
    # Efforts
    certifications = models.JSONField(default=list)
    looking_for_career_switch = models.BooleanField(default=False)
    willing_to_take_projects = models.BooleanField(default=False)
    interested_in_new_course = models.BooleanField(default=False)
    
    # Final Stage
    portfolio_link = models.URLField()
    ideal_organization = models.CharField(max_length=200)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Profile - {self.current_occupation}"
    






class newmodel(models.Model):
    """
    Model representing the admin dashboard.
    """
    # Define fields for the admin dashboard model here
    # For example:
    total_users = models.CharField(max_length=30,default=0)
    total_posts = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)

    def __str__(self):
        return f"Admin Dashboard - Users: {self.total_users}, Posts: {self.total_posts}, Comments: {self.total_comments}"