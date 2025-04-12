from django.db import models

# Create your models here.


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