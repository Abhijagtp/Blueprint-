from django.contrib import admin

# Register your models here.


from .models import Email, CustomUser

admin.site.register(Email)
admin.site.register(CustomUser)