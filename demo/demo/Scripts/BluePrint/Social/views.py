from django.shortcuts import render

# Create your views here.
# views.py
from django.shortcuts import render
from django.db.models import Count, Q, Sum
from django.db.models.functions import TruncDay
from datetime import datetime, timedelta
from Users.models import Post, Like, Comment, FollowRequest, Message
from django.contrib.auth.decorators import login_required
import json

@login_required
def dashboard_view(request):
    user = request.user
    user_profile = user.userprofile  # Assuming UserProfile is linked to CustomUser

    # Date range filter (default: last 30 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    date_filter = request.GET.get('date_range', '30')
    if date_filter == '7':
        start_date = end_date - timedelta(days=7)
    elif date_filter == '90':
        start_date = end_date - timedelta(days=90)

    # Post type filter
    post_type = request.GET.get('post_type', 'all')

    # Base query for posts
    posts_query = Post.objects.filter(user_profile=user_profile)
    if post_type != 'all':
        posts_query = posts_query.filter(content_type=post_type)
    if start_date and end_date:
        posts_query = posts_query.filter(created_at__range=[start_date, end_date])

    # Overview Metrics
    total_posts = posts_query.count()
    total_likes = Like.objects.filter(post__user_profile=user_profile).count()
    total_comments = Comment.objects.filter(post__user_profile=user_profile).count()
    
    # Follower counts (incoming and outgoing)
    incoming_followers = FollowRequest.objects.filter(to_user=user, status='accepted').count()
    outgoing_follows = FollowRequest.objects.filter(from_user=user, status='accepted').count()
    total_followers = incoming_followers + outgoing_follows

    # Messages
    total_messages_sent = Message.objects.filter(sender=user).count()
    total_messages_received = Message.objects.filter(receiver=user).count()
    total_messages = total_messages_sent + total_messages_received

    # Saved posts
    total_saved_posts = user_profile.saved_posts.count()

    # Engagement over time (likes and comments per day)
    engagement_data = (
        Post.objects.filter(user_profile=user_profile, created_at__range=[start_date, end_date])
        .annotate(date=TruncDay('created_at'))
        .values('date')
        .annotate(likes_count=Count('likes'), comments_count=Count('comments'))
        .order_by('date')
    )
    engagement_dates = [entry['date'].strftime('%Y-%m-%d') for entry in engagement_data]
    likes_data = [entry['likes_count'] for entry in engagement_data]
    comments_data = [entry['comments_count'] for entry in engagement_data]

    # Follower growth over time
    follower_growth_data = (
        FollowRequest.objects.filter(
            Q(to_user=user, status='accepted') | Q(from_user=user, status='accepted'),
            created_at__range=[start_date, end_date]
        )
        .annotate(date=TruncDay('created_at'))
        .values('date')
        .annotate(followers_count=Count('id'))
        .order_by('date')
    )
    follower_dates = [entry['date'].strftime('%Y-%m-%d') for entry in follower_growth_data]
    follower_counts = [entry['followers_count'] for entry in follower_growth_data]

    # Post type distribution
    post_types_data = (
        Post.objects.filter(user_profile=user_profile)
        .values('content_type')
        .annotate(count=Count('id'))
    )
    post_types_labels = [entry['content_type'].capitalize() for entry in post_types_data]
    post_types_counts = [entry['count'] for entry in post_types_data]

    # Recent Activity
    recent_likes = Like.objects.filter(post__user_profile=user_profile).select_related('user_profile__user', 'post').order_by('-created_at')[:5]
    recent_comments = Comment.objects.filter(post__user_profile=user_profile).select_related('user_profile__user', 'post').order_by('-created_at')[:5]
    recent_messages = Message.objects.filter(Q(sender=user) | Q(receiver=user)).select_related('sender', 'receiver', 'post').order_by('-timestamp')[:5]

    context = {
        'total_posts': total_posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_followers': total_followers,
        'total_messages': total_messages,
        'total_saved_posts': total_saved_posts,
        'engagement_dates': json.dumps(engagement_dates),
        'likes_data': json.dumps(likes_data),
        'comments_data': json.dumps(comments_data),
        'follower_dates': json.dumps(follower_dates),
        'follower_counts': json.dumps(follower_counts),
        'post_types_labels': json.dumps(post_types_labels),
        'post_types_counts': json.dumps(post_types_counts),
        'recent_likes': recent_likes,
        'recent_comments': recent_comments,
        'recent_messages': recent_messages,
        'date_filter': date_filter,
        'post_type': post_type,
    }
    return render(request, 'dashboard_social.html', context)