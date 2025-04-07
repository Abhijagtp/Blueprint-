from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   path('admin_dashboard/', views.dashboard_view, name='admin_dashboard'),
]