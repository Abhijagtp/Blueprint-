from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   path('', views.admin_login, name='admin_login'),
   path('admin_dashboard/', views.dashboard_view, name='admin_dashboard'),
   path('analytics/', views.analytics_view, name='analytics'),
   path('analytics_blog/', views.analytics_blog_view, name='analytics_blog'),
   path('organization_post_blog', views.organization_blog_view, name='organization_post_blog'),
   path('organization_invoice/', views.organization_invoice_view, name='organization_invoice'),
   path('user_management/', views.user_management_view, name='user_management'),
   path('organization/', views.organization_view, name='organization'),
   path('organization_project_details/', views.organization_project_view, name='organization_project_details'),
   path('mentor_user/', views.mentor_user_view, name='mentor_user'),
   path('mentor_course_details/', views.mentor_course_details_view, name='mentor_course_details'),
   path('project_moderation/', views.project_moderation_view, name='project_moderation'),
   path('content_moderation/', views.content_moderation_view, name='content_moderation'),
   path('service_desk_add/', views.service_desk_add_view, name='service_desk_add'),
   path('admin/login/', views.AdminLoginView.as_view(), name='admin_login')
]