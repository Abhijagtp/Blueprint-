from django.contrib import admin

# Register your models here.

from .models import Project, ProjectRequest

admin.site.register(Project)

admin.site.register(ProjectRequest)