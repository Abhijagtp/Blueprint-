"""
URL configuration for BluePrint project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [

    
    path("training/", views.training_view, name="traning"),
    path("learning/", views.my_learning_view, name="learning"),
    path('create-course/', views.create_course, name='create_course'),
    path('course/<slug:slug>/', views.course_detail, name='course_detail'),
    path('enroll/<int:course_id>/', views.enroll_course, name='enroll_course'),
    path('update-progress/', views.update_progress, name='update_progress'),

    path('my-courses/', views.my_courses_view, name='my_courses'),  # My Courses Page
    path('course/edit/<int:course_id>/', views.edit_course_view, name='edit_course'),  # Edit Course
    path('course/delete/<int:course_id>/', views.delete_course_view, name='delete_course'),  # Delete Course

    # cart 

    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('course/<int:course_id>/buy/', views.buy_course, name='buy_course'),
]

    
