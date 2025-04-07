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

   path('digitalassets/',views.digitalassets_view, name='digitalassets'),
   
   path('ibw/',views.ibw_view, name='ibw'),
   path('blogs/',views.blogs_views, name='Blogs'),
   path('whitepaper/',views.Whitepaper_view, name='Whitepapers'),
#    insights 

   path('save-insight/', views.save_insight, name='save_insight'),
#    drafts 

    # blogs 
    path('save-blog/', views.save_blog, name='save_blog'),
    
    # whitepapers 
    path('save-whitepaper/', views.save_whitepaper, name='save_whitepaper'),


    # main page 
   path('get-assets/', views.get_assets, name='get_assets'),
    path('get-blog/<int:blog_id>/', views.get_blog, name='get_blog'),
    path('delete-blog/<int:blog_id>/', views.delete_blog, name='delete_blog'),
    path('get-whitepaper/<int:whitepaper_id>/', views.get_whitepaper, name='get_whitepaper'),
    path('delete-whitepaper/<int:whitepaper_id>/', views.delete_whitepaper, name='delete_whitepaper'),
    path('get-insight/<int:insight_id>/', views.get_insight, name='get_draft'),
    path('delete-insight/<int:insight_id>/', views.delete_insight, name='delete_draft'),
    path('view-all-assets/', views.view_all_assets_view, name='view_all_assets'),
    
    # view asset    
    path('view-asset/<str:asset_type>/<int:asset_id>/', views.view_asset, name='view_asset'),
    path('edit-asset/<str:asset_type>/<int:asset_id>/', views.edit_asset, name='edit_asset'),
    # Detail page 
    path('blog/<int:blog_id>/', views.blog_detail, name='blog_detail'),
    path('whitepaper/<int:whitepaper_id>/', views.whitepaper_detail, name='whitepaper_detail'),
    path('insight/<int:insight_id>/', views.insight_detail, name='insight_detail'),

]

