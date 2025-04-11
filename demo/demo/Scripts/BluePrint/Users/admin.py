from django.contrib import admin

# Register your models here.
from .models import CustomUser, UserProfile, Experience, Education, Skill, Certification,ChatGroup,GroupMessage,Post

admin.site.register(ChatGroup)
admin.site.register(Post)
admin.site.register(UserProfile)