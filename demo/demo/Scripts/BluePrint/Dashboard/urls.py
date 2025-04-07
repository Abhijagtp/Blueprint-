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
from Dashboard import views

urlpatterns = [

    

    path("get-unread-messages/", views.get_unread_messages, name="get_unread_messages"),
    
    path('emails/', views.inbox, name='inbox'),
    path('sent/', views.sent_emails, name='sent_emails'),
    path('archive/', views.archive_emails, name='archive_emails'),
    path('starred/', views.starred_emails, name='starred_emails'),
    path('unread/', views.unread_emails, name='unread_emails'),
    path('emails/<int:email_id>/archive/', views.archive_email, name='archive_email'),
    path('emails/<int:email_id>/unarchive/', views.unarchive_email, name='unarchive_email'),
    path('emails/<int:email_id>/star/', views.star_email, name='star_email'),
    path('emails/<int:email_id>/mark_as_read/', views.mark_as_read, name='mark_as_read'),
    path('emails/<int:email_id>/mark_as_unread/', views.mark_as_unread, name='mark_as_unread'),
    path('emails/<int:email_id>/delete/', views.delete_email, name='delete_email'),
    path('emails/<int:email_id>/', views.get_email, name='get_email'),
    path('emails/<int:email_id>/replies/', views.get_replies, name='get_replies'),
    path('send/', views.send_email, name='send_email'),
    path('reply/', views.reply_email, name='reply_email'),
    path('dashboard_new/', views.dashboard, name='dashboard_new'),
   

    
]
