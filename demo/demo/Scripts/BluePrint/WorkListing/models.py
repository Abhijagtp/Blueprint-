from django.db import models

# Create your models here.

from Users.models import CustomUser

# Project Model
class Project(models.Model):
    org = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='posted_projects', limit_choices_to={'user_type': 'organizational'})
    domain = models.CharField(max_length=255)
    description = models.TextField()
    experience_required = models.IntegerField()
    skills_required = models.JSONField(default=list)
    submission_date = models.DateField()
    payment = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)  # Project is active or not
    applications_open = models.BooleanField(default=True)  # ✅ Track whether applications are open

    def __str__(self):
        return f"{self.domain} - {self.org.username}"



# Project Request Model
class ProjectRequest(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='requests')
    professional = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='project_requests', limit_choices_to={'user_type': 'professional'})
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    requested_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return f"{self.professional.username} - {self.project.domain} - {self.status}"
    

class ProjectSubmission(models.Model):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

    STATUS_CHOICES = [
        (PENDING, 'Pending'),
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
    ]

    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]

    project_request = models.ForeignKey(ProjectRequest, on_delete=models.CASCADE, related_name='submissions')
    submission_url = models.URLField(blank=True, null=True)
    submission_file = models.FileField(upload_to='submissions/', blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=PENDING)
    rating = models.IntegerField(choices=RATING_CHOICES, blank=True, null=True)  # New field
    feedback = models.TextField(blank=True, null=True)  # New field
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True, related_name='evaluated_submissions', limit_choices_to={'user_type': 'organizational'})

    def __str__(self):
        return f"Submission for {self.project_request.project.domain} by {self.project_request.professional.username}"

    class Meta:
        unique_together = ('project_request',)  # One submission per approved request