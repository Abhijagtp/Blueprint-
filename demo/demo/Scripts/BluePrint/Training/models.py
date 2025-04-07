from django.db import models

# Create your models here.
from django.utils.text import slugify

from django.db import models
from django.utils.text import slugify
from Users.models import CustomUser

from django.db import models
from django.utils.text import slugify
from decimal import Decimal

class Course(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
    ]

    CATEGORY_CHOICES = [
        ('development', 'Development'),
        ('business', 'Business'),
        ('finance', 'Finance & Accounting'),
        ('it_software', 'IT & Software'),
        ('office_productivity', 'Office Productivity'),
        ('personal_development', 'Personal Development'),
        ('design', 'Design'),
        ('marketing', 'Marketing'),
        ('lifestyle', 'Lifestyle'),
        ('photography_video', 'Photography & Video'),
        ('health_fitness', 'Health & Fitness'),
        ('music', 'Music'),
        ('teaching_academics', 'Teaching & Academics'),
    ]

    instructor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='courses')
    title = models.CharField(max_length=255)
    subtitle = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    overview = models.TextField()
    thumbnail = models.ImageField(upload_to='course_thumbnails/')
    featured_video = models.FileField(upload_to='featured_videos/', null=True, blank=True)
    level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ])
    
    prerequisites = models.TextField()
    skills = models.TextField(help_text="List of skills covered in the course", blank=True)
    
    
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    
    is_free = models.BooleanField(default=False)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('title', 'instructor')  # Prevents duplicate course names for the same instructor

    def save(self, *args, **kwargs):
        # Ensure unique slug generation
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            count = 1
            while Course.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{count}"
                count += 1
            self.slug = slug

        # If the course is marked free, ensure the price is 0
        if self.is_free:
            self.price = Decimal(0)
            self.discount = Decimal(0)  # No discount for free courses

        super().save(*args, **kwargs)

    @property
    def discounted_price(self):
        """Returns the final price after applying the discount."""
        return max(Decimal(self.price) - Decimal(self.discount or 0), Decimal(0))

    def __str__(self):
        return self.title
    
    @property
    def total_duration(self):
        total_seconds = sum(lesson.duration.total_seconds() for lesson in self.lessons.all())
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        
        if minutes == 0:
            return f"{hours} hours"
        elif hours == 0:
            return f"{minutes} minutes"
        else:
            return f"{hours} hours {minutes} minutes"

    
  

  



# Lesson Model
class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=255)
    description = models.TextField()
    video = models.FileField(upload_to='lesson_videos/')
    duration = models.DurationField() 
    created_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        if self.duration.total_seconds() > 3600:
            raise ValueError("Lesson duration cannot exceed 1 hour.")
        super().save(*args, **kwargs)

        
    def __str__(self):
        return f"{self.course.title} - {self.title}"
    


from django.db import models
from decimal import Decimal
from django.utils.text import slugify

class Enrollment(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)  # In case users can be unenrolled

    class Meta:
        unique_together = ('user', 'course')  # Prevents duplicate enrollments

    def __str__(self):
        return f"{self.user.username} enrolled in {self.course.title}"
    


from django.db import models
from django.conf import settings
from .models import Course, Lesson

class LessonProgress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson')  # Ensure one progress record per lesson and user

    def __str__(self):
        return f"{self.user.username} - {self.lesson.title} - {'Completed' if self.completed else 'Not Completed'}"




class CartItem(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='cart_items')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'course')
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"