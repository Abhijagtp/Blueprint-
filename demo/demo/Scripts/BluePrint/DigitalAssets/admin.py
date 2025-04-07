from django.contrib import admin

# Register your models here.

from . models import Blog, Whitepaper,Insight

admin.site.register(Blog)
admin.site.register(Whitepaper)
admin.site.register(Insight)