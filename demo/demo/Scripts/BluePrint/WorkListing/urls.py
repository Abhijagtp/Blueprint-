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
   path('work_listing/', views.work_listing, name='work_listing'),
   path('explore_projects/', views.explore_projects, name='explore_projects'),
   path('application_status/', views.application_status, name='application_status'),
   path('project_status/', views.project_status, name='project_status'),
   path('invoice/', views.invoice, name='invoice'),
   path('search_talent/', views.search_talent, name='search_talent'),
   path('post_project/',views.post_project,name='post_project'),
   path("create-project/", views.create_project, name="create_project"),
   path('get_project/<int:project_id>/', views.get_project, name='get_project'),
   path("apply_project/<int:project_id>/", views.apply_project, name="apply_project"),
   path('project/<int:project_id>/applicants/', views.project_applicants, name='project_applicants'),
   path("update-application-status/", views.update_application_status, name="update_application_status"),
   path('project/<int:project_id>/toggle-applications/', views.toggle_project_applications, name='toggle_project_applications'),
   path("submit-project/<int:project_id>/", views.submit_project, name="submit_project"),
   path('project_approval/', views.project_approval, name='project_approval'),
   path('evaluate/<int:submission_id>/', views.evaluate_project, name='evaluate_project'),
]

