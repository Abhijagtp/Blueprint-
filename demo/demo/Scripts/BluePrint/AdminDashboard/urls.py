from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   path('admin_dashboard/', views.dashboard_view, name='admin_dashboard'),
   path('analytics/', views.analytics_view, name='analytics'),
   path('user_management/', views.user_management_view, name='user_management'),
   path('organization/', views.organization_view, name='organization'),
]