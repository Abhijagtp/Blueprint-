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

from Users import views 
from .views import market_data_view, fetch_sector_performance, chat_list, chat_room, send_message


urlpatterns = [
    

    path('ajax/search/', views.ajax_search, name='ajax_search'),
    path('',views.home,name='home'),
 
    path('user_selection/',views.user_selection,name='user_selection'),
    path('user_type_selection/',views.user_type_selection_view,name='user_type_selection'),
    path('register/',views.register,name='register'),
    path('login/',views.login_view,name='login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('set-new-password/', views.set_new_password, name='set_new_password'),

    path('logout/',views.logout_view,name='logout'),
    path('profile/',views.profile_view,name='profile'),
    path('profile/<str:username>/', views.profile_view, name='profile_detail'),
    path('save_profile/', views.save_profile, name='save_profile'),
    path('update_profile_image/', views.update_profile_image, name='update_profile_image'),
    path('update_cover_image/', views.update_cover_image, name='update_cover_image'),
    path('load_tab_content/', views.load_tab_content, name='load_tab_content'),
    path('load_posts_content/', views.load_posts_content, name='load_posts_content'),
    path('load_experience/', views.load_experience, name='load_experience'),
    path('load_education/', views.load_education, name='load_education'),
    path('load_skills/', views.load_skills, name='load_skills'),
    path('load_certifications/', views.load_certifications, name='load_certifications'),
    path('load_projects/', views.load_projects, name='load_projects'),
    path('load_courses/', views.load_courses, name='load_courses'),
    path('update_organization/<int:org_id>/', views.update_organization, name='update_organization'),
    path('load_posts/', views.load_posts, name='load_posts'),
    path('load_about/', views.load_about, name='load_about'),

    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    

    path('save_experience/', views.save_experience, name='save_experience'),
    path('experience/edit/<int:experience_id>/', views.edit_experience, name='edit_experience'),
    path('experience/delete/<int:experience_id>/', views.delete_experience, name='delete_experience'),
    path('education/add/', views.add_education, name='add_education'),
    path('education/update/<int:education_id>/', views.edit_education, name='edit_education'),
    path('education/delete/<int:education_id>/', views.delete_education, name='delete_education'),
    path("add-skill/", views.add_skill, name="add_skill"),
    path("update-skill/<int:skill_id>/", views.update_skill, name="update_skill"),
    path("delete-skill/<int:skill_id>/", views.delete_skill, name="delete_skill"),

    path('add-certification/', views.add_certification, name='add_certification'),
    path("edit-certification/<int:cert_id>/", views.edit_certification, name="edit_certification"),
    path("delete-certification/<int:cert_id>/", views.delete_certification, name="delete_certification"),

    path('add/', views.add_project, name='add_project'),
    path('edit/<int:project_id>/', views.edit_project, name='edit_project'),
    path('delete/<int:project_id>/', views.delete_project, name='delete_project'),

    path("create_post/", views.create_post, name="create_post"),
    path('get-new-posts/', views.get_new_posts, name='get_new_posts'),
    path("delete-post/<int:post_id>/", views.delete_post, name="delete_post"),
    path("get-followers/", views.get_followers, name="get_followers"),
    path("send-post-share/", views.send_post_share, name="send_post_share"),
    path("get-post-content/<int:post_id>/", views.get_post_content, name="get_post_content"),
    path("timeline",views.timeline_view,name="timeline"),
    path('toggle_like/<int:post_id>/', views.toggle_like, name='toggle_like'),
    path('add_comment/<int:post_id>/', views.add_comment, name='add_comment'),
    path("get-replies/<int:comment_id>/",views.get_replies, name="get_replies"),
    path('get-following-user-ids/', views.get_following_user_ids, name='get_following_user_ids'),
    path('check-follow-connections/', views.check_follow_connections, name='check_follow_connections'),
   
    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
    path("followers/<str:username>/", views.followers_list, name="followers_list"),
    path('requests/', views.follow_requests_view, name='requests'),
    path('saved_posts/', views.saved_posts, name='saved_posts'),
    path('save_post/<int:post_id>/', views.save_post, name='save_post'),
    path('unsave_post/<int:post_id>/', views.unsave_post, name='unsave_post'),
    path('load_more_posts/', views.load_more_posts, name='load_more_posts'),
    
    
    path('send-follow-request/<int:user_id>/', views.send_follow_request, name='send_follow_request'),
    path('accept-follow-request/<int:request_id>/', views.accept_follow_request, name='accept_follow_request'),
    path('decline-follow-request/<int:request_id>/', views.decline_follow_request, name='decline_follow_request'),
    path('unfollow-user/<int:user_id>/', views.unfollow_user, name='unfollow_user'),

    # chat message 
    path("messages/", chat_list, name="chat_list"),
    path("messages/<str:username>/", chat_room, name="chat_room"),
    path("send-message/", send_message, name="send_message"),
    path("create-group/", views.create_group, name="create_group"),
    path("chat/group/<str:group_name>/", views.chat_group_room, name="chat_group_room"),
    path("group/<int:group_id>/remove_member/<int:member_id>/", views.remove_group_member, name="remove_group_member"),
    path("group/<int:group_id>/leave/", views.leave_group, name="leave_group"),
    path("group/<int:group_id>/add_members/", views.add_group_members, name="add_group_members"),
    path("ajax/search_users/", views.search_users, name="search_users"),
    path("ajax/search_users/", views.ajax_search_users, name="ajax_search_users"),
    path("update_group_details/<int:group_id>/", views.update_group_details, name="update_group_details"),
    path("delete_group/<int:group_id>/", views.delete_group, name="delete_group"),
    path('get-follower-user-ids/', views.get_follower_user_ids, name='get_follower_user_ids'),

    # form 
    path('organization-form/', views.organization_form, name='organization_form'),
    path('submit-organization/', views.submit_organization, name='submit_organization'),
    path('user_form',views.user_form,name='user_form'),
    path('get-specializations/', views.get_specializations, name='get_specializations'),



    #Raise Ticket Section
    path('userraiseticket', views.userraiseticket, name='userraiseticket'),

]
