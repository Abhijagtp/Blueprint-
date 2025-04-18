from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
   path('', views.admin_login, name='admin_login'),
   path('admin_dashboard/', views.dashboard_view, name='admin_dashboard'),
   path('analytics/', views.analytics_view, name='analytics'),
   path('analytics_blog/<post_id>', views.analytics_blog_view, name='analytics_blog'),
   path('organization_post_blog', views.organization_blog_view, name='organization_post_blog'),
   path('organization_invoice/', views.organization_invoice_view, name='organization_invoice'),
   path('user_management/', views.user_management_view, name='user_management'),
   path('update-account-status/', views.update_account_status, name='update_account_status'),
   path('user_manage_user_details/<int:user_id>/', views.user_manage_user_details_view, name='user_manage_user_details'),
   path('organization/', views.organization_view, name='organization'),
   path('organization_project_details/<int:project_id>', views.organization_project_view, name='organization_project_details'),
   path('mentor_user/', views.mentor_user_view, name='mentor_user'),
   path('mentor_course_details/<int:course_id>', views.mentor_course_details_view, name='mentor_course_details'),
   path('project_moderation/', views.project_moderation_view, name='project_moderation'),
   path('project/remove/', views.remove_projects, name='remove_projects'),
   path('content_moderation/', views.content_moderation_view, name='content_moderation'),
   path('moderation/remove/', views.remove_posts, name='remove_posts'),
   path('service_desk_add/', views.service_desk_add_view, name='service_desk_add'),
   path('admin/login/', views.AdminLoginView.as_view(), name='admin_login')
]