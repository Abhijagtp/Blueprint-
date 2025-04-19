from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Users.models import CustomUser
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
from django.views.decorators.http import require_POST
import calendar
from collections import Counter
from django.db.models import Q
from collections import OrderedDict
from dateutil.relativedelta import relativedelta

# Create your views here.
@login_required
def dashboard_view(request):
    CustomUser = get_user_model()
    today = now()

    selected_month = int(request.GET.get('month', today.month))
    selected_year = today.year
    if selected_month > today.month:
        selected_year -= 1 

    start_selected = datetime(selected_year, selected_month, 1)
    _, last_day = calendar.monthrange(selected_year, selected_month)
    end_selected = datetime(selected_year, selected_month, last_day, 23, 59, 59)

    # Previous month range for comparison
    prev_month = selected_month - 1 or 12
    prev_year = selected_year - 1 if prev_month == 12 else selected_year
    start_prev = datetime(prev_year, prev_month, 1)
    _, last_day_prev = calendar.monthrange(prev_year, prev_month)
    end_prev = datetime(prev_year, prev_month, last_day_prev, 23, 59, 59)

    # Count for current and previous month
    current_month_users = CustomUser.objects.filter(date_joined__range=(start_selected, end_selected)).count()
    previous_month_users = CustomUser.objects.filter(date_joined__range=(start_prev, end_prev)).count()

    # Logins this month (main point)
    current_month_logins = CustomUser.objects.filter(last_login__range=(start_selected, end_selected)).count()

    # Generate monthly login counts for the past 12 months
    monthly_login_labels = []
    monthly_login_counts = []

    for i in range(11, -1, -1):  # Last 12 months
        month_date = today - relativedelta(months=i)
        start = datetime(month_date.year, month_date.month, 1)
        _, last_day = calendar.monthrange(month_date.year, month_date.month)
        end = datetime(month_date.year, month_date.month, last_day, 23, 59, 59)

        count = CustomUser.objects.filter(
            last_login__range=(start, end),
            is_superuser=False
        ).count()

        monthly_login_labels.append(calendar.month_abbr[month_date.month])
        monthly_login_counts.append(count)

    if previous_month_users == 0:
        percent_change = 100
    else:
        percent_change = ((current_month_users - previous_month_users) / previous_month_users) * 100

    months = [{'value': i, 'label': calendar.month_name[i]} for i in range(1, 13)]
    selected_month_label = calendar.month_name[selected_month]

    context = {
        'current_month_users': current_month_users,
        'percent_change': round(percent_change, 1),
        'percent_change_abs': abs(round(percent_change, 1)),
        'selected_month': selected_month,
        'selected_month_label': selected_month_label,
        'months': months,
        'monthly_logins': current_month_logins,
        'monthly_login_labels': monthly_login_labels,  # For graph X-axis
        'monthly_login_counts': monthly_login_counts,  # For graph Y-axis
    }



    return render(request, 'admin_dashboard.html', context)


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import Coalesce
from Users.models import CustomUser, UserProfile, Post, Like, Comment
from Training.models import Course
from WorkListing.models import Project, ProjectRequest
from DigitalAssets.models import Blog, Whitepaper, Insight

@login_required
def analytics_view(request):
    """
    View for Admin Analytics.
    Displays searched profiles and posts for all users, with an option to filter by user type.
    Calculates impressions based on likes, comments, and saves.
    Fetches titles for Blog, Whitepaper, and Insight posts.
    """
    # Check if the user is an admin
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    # Get the user type filter from query parameters
    selected_user_type = request.GET.get('user_type', None)

    # Filter users based on the selected user type
    users = CustomUser.objects.all()
    if selected_user_type:
        users = users.filter(user_type=selected_user_type)

    # Searched Profiles Data
    searched_profiles = []
    for user in users:
        user_profile = user.userprofile
        # Calculate impressions based on likes, comments, and saves
        posts = Post.objects.filter(user_profile=user_profile).annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
            saves_count=Count('saved_by')
        )

        # Sum the weighted metrics to calculate impressions
        impressions = sum(
            (post.likes_count * 2) + (post.comments_count * 3) + (post.saves_count * 5)
            for post in posts
        )

        # Total likes on all posts
        total_likes = Like.objects.filter(post__user_profile=user_profile).count()

        # Digital assets (e.g., number of posts, blogs, whitepapers, insights, courses)
        digital_assets = (
            user_profile.posts.count() +
            user_profile.blogs.count() +
            user_profile.whitepapers.count() +
            user_profile.insights.count()
        )
        if user.user_type == CustomUser.INSTRUCTOR:
            digital_assets += Course.objects.filter(instructor=user).count()

        # Projects completed
        if user.user_type == CustomUser.PROFESSIONAL:
            # For professionals: count accepted project requests
            projects_completed = ProjectRequest.objects.filter(
                professional=user,
                status='accepted'
            ).count()
        elif user.user_type == CustomUser.ORGANIZATIONAL:
            # For organizations: count completed projects
            projects_completed = Project.objects.filter(org=user, is_active=False).count()
        elif user.user_type == CustomUser.INSTRUCTOR:
            # For instructors: count submitted courses
            projects_completed = Course.objects.filter(instructor=user, status='submitted').count()
        else:
            projects_completed = 0

        searched_profiles.append({
            'user': user,
            'impressions': impressions,
            'total_likes': total_likes,
            'digital_assets': digital_assets,
            'projects_completed': projects_completed,
        })

    # Sort by impressions in descending order and limit to 9 entries
    searched_profiles = sorted(searched_profiles, key=lambda x: x['impressions'], reverse=True)[:9]

    # Posts Data
    posts_query = Post.objects.all()
    if selected_user_type:
        posts_query = posts_query.filter(user_profile__user__user_type=selected_user_type)
    
    posts = posts_query.annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments')
    ).order_by('-likes_count')[:9]

    # Fetch titles for Blog, Whitepaper, and Insight posts
    for post in posts:
        if post.content_type == 'blog' and post.content_id:
            try:
                blog = Blog.objects.get(id=post.content_id)
                post.blog_title = blog.title
            except Blog.DoesNotExist:
                post.blog_title = "(Untitled Blog)"
        elif post.content_type == 'whitepaper' and post.content_id:
            try:
                whitepaper = Whitepaper.objects.get(id=post.content_id)
                post.whitepaper_title = whitepaper.title
            except Whitepaper.DoesNotExist:
                post.whitepaper_title = "(Untitled Whitepaper)"
        elif post.content_type == 'insight' and post.content_id:
            try:
                insight = Insight.objects.get(id=post.content_id)
                post.insight_title = insight.title
            except Insight.DoesNotExist:
                post.insight_title = "(Untitled Insight)"
        else:
            # For normal posts, ensure caption is not None
            post.caption = post.caption or "(Untitled)"

    context = {
        'searched_profiles': searched_profiles,
        'posts': posts,
        'selected_user_type': selected_user_type,
    }
    return render(request, 'analytics.html', context)

@login_required
def analytics_blog_view(request, post_id):
    """
    View for detailed analytics of a specific post.
    Accessible only to admin users.
    Fetches the appropriate content for Blog, Whitepaper, and Insight posts.
    """
    # Check if the user is an admin
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    post = get_object_or_404(Post, id=post_id)
    likes_count = post.likes.count()
    comments_count = post.comments.count()

    # Fetch the content for Blog, Whitepaper, or Insight
    content = None
    content_title = post.caption or "(Untitled)"
    if post.content_type == 'blog' and post.content_id:
        content = get_object_or_404(Blog, id=post.content_id)
        content_title = content.title
    elif post.content_type == 'whitepaper' and post.content_id:
        content = get_object_or_404(Whitepaper, id=post.content_id)
        content_title = content.title
    elif post.content_type == 'insight' and post.content_id:
        content = get_object_or_404(Insight, id=post.content_id)
        content_title = content.title

    context = {
        'post': post,
        'content': content,
        'content_title': content_title,
        'likes_count': likes_count,
        'comments_count': comments_count,
    }
    return render(request, 'analyticspostblog.html', context)



@login_required
def organization_blog_view(request):
    return render(request, 'organaizationpostblog.html')

@login_required
def organization_invoice_view(request):
    return render(request, 'organization_invoice.html')

@login_required
def user_management_view(request):
    users = CustomUser.objects.all().order_by('-date_joined') 
    service_desk_users = CustomUser.objects.all().order_by('-date_joined') 
    return render(request, 'user_management.html', {
        'users': users,
        'service_desk_users': service_desk_users
    })

@login_required
def update_account_status(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        new_status = request.POST.get('account_status')
        duration_days = request.POST.get('suspend_duration_days')

        user = get_object_or_404(CustomUser, pk=user_id)
        user.account_status = new_status

        if new_status == "Open":
            user.is_active = True
            user.suspended_until = None

        elif new_status == "Suspend":
            user.is_active = False
            if duration_days:
                user.suspended_until = timezone.now() + timedelta(days=int(duration_days))

        elif new_status == "Deactivate":
            user.is_active = False
            user.suspended_until = None

        user.save()
        messages.success(request, f"Account status for {user.username} updated to {new_status}.")

    return redirect('user_management')  

@login_required
def user_manage_user_details_view(request,user_id):
    return render(request, 'user_manage_user_details.html')



from django.db.models import Count, Q
@login_required
def organization_view(request):
    """
    View for Organization Analytics.
    Displays projects, posts, and invoices for organizational users.
    Includes search functionality to filter projects by organization name.
    Determines the assigned professional for each project based on accepted ProjectRequest.
    """
    # Check if the user is an admin
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    # Get the search query from the request
    search_query = request.GET.get('search', '')

    # Fetch organizational users
    org_users = CustomUser.objects.filter(user_type=CustomUser.ORGANIZATIONAL)

    # Projects Data
    projects_query = Project.objects.filter(org__in=org_users).select_related('org__userprofile')
    if search_query:
        projects_query = projects_query.filter(
            Q(org__first_name__icontains=search_query) |
            Q(org__last_name__icontains=search_query)
        )
    projects = projects_query.order_by('-created_at')[:9]  # Limit to 9 entries

    # Attach the assigned professional to each project
    for project in projects:
        accepted_request = ProjectRequest.objects.filter(project=project, status='accepted').first()
        project.assigned_professional = accepted_request.professional if accepted_request else None

    # Posts Data
    posts_query = Post.objects.filter(user_profile__user__in=org_users).annotate(
        likes_count=Count('likes'),
        comments_count=Count('comments')
    )
    posts = posts_query.order_by('-likes_count')[:9]  # Limit to 9 entries

    # Fetch titles for Blog, Whitepaper, and Insight posts
    for post in posts:
        if post.content_type == 'blog' and post.content_id:
            try:
                blog = Blog.objects.get(id=post.content_id)
                post.blog_title = blog.title
            except Blog.DoesNotExist:
                post.blog_title = "(Untitled Blog)"
        elif post.content_type == 'whitepaper' and post.content_id:
            try:
                whitepaper = Whitepaper.objects.get(id=post.content_id)
                post.whitepaper_title = whitepaper.title
            except Whitepaper.DoesNotExist:
                post.whitepaper_title = "(Untitled Whitepaper)"
        elif post.content_type == 'insight' and post.content_id:
            try:
                insight = Insight.objects.get(id=post.content_id)
                post.insight_title = insight.title
            except Insight.DoesNotExist:
                post.insight_title = "(Untitled Insight)"
        else:
            post.caption = post.caption or "(Untitled)"

    # Invoices Data
    
    context = {
        'projects': projects,
        'posts': posts,
       
        'search_query': search_query,
    }
    return render(request, 'organization_user.html', context)

@login_required
def organization_project_view(request, project_id):
    """
    View for Organization Project Details.
    Displays detailed information about a specific project, including assigned professional and invoice status.
    """
    # Check if the user is an admin
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    # Fetch the project with related userprofile for the profile image
    project = get_object_or_404(Project.objects.select_related('org__userprofile'), id=project_id)

    # Process the skills_required field into a list
    if project.skills_required:
        project.skills_list = [skill.strip() for skill in project.skills_required.split(',')]
    else:
        project.skills_list = []

    # Determine the assigned professional
    accepted_request = ProjectRequest.objects.filter(project=project, status='accepted').first()
    project.assigned_professional = accepted_request.professional if accepted_request else None

    # Determine the invoice status
    # Assuming an Invoice model exists with a project field
    

    # Debug: Print the skills_required and skills_list to confirm the data
    print(f"Skills for project {project.id}: {project.skills_required}")
    print(f"Skills list for project {project.id}: {project.skills_list}")

    return render(request, 'organization_project_details.html', {
        'project': project,
    })

@login_required
def organization_post_blog_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if not request.user.is_staff:
        return render(request, '403.html', status=403)
    likes_count = post.likes.count()
    comments_count = post.comments.count()
    content = None
    content_title = post.caption or "(Untitled)"
    if post.content_type == 'blog' and post.content_id:
        content = get_object_or_404(Blog, id=post.content_id)
        content_title = content.title
    elif post.content_type == 'whitepaper' and post.content_id:
        content = get_object_or_404(Whitepaper, id=post.content_id)
        content_title = content.title
    elif post.content_type == 'insight' and post.content_id:
        content = get_object_or_404(Insight, id=post.content_id)
        content_title = content.title
    return render(request, 'organization_post_blog.html', {
        'post': post,
        'content': content,
        'content_title': content_title,
        'likes_count': likes_count,
        'comments_count': comments_count,
    })

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, Count, Avg
from Users.models import CustomUser
from Training.models import Course, Enrollment, LessonProgress
from django.utils import timezone


@login_required
def mentor_user_view(request):
    """
    View for Mentor Analytics.
    Displays courses and mentee data for mentors.
    Includes search functionality to filter courses by title and mentors by name.
    """
    # Check if the user is an admin
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    # Get search queries from the request
    course_search_query = request.GET.get('course_search', '')
    mentee_search_query = request.GET.get('mentee_search', '')

    # Debug: Check all courses in the database
    all_courses = Course.objects.all()
    print(f"Total courses in database: {all_courses.count()}")
    if all_courses.exists():
        print(f"All course titles: {[course.title for course in all_courses]}")
    else:
        print("No courses in the database.")

    # Fetch all instructors (previously mentors)
    mentors = CustomUser.objects.filter(user_type='instructor')  # Changed from 'mentor' to 'instructor'
    print(f"Number of instructors: {mentors.count()}")
    if mentors.exists():
        print(f"Instructors: {[mentor.get_full_name() for mentor in mentors]}")
    else:
        print("No instructors found.")

    # Debug: Check the instructor IDs of all courses
    course_instructors = Course.objects.values('instructor__id', 'instructor__user_type').distinct()
    print(f"Course instructors: {list(course_instructors)}")

    # --- Courses Section ---
    # Fetch all courses by instructors
    courses_query = Course.objects.filter(instructor__in=mentors).select_related('instructor')
    print(f"Number of courses for instructors (before search): {courses_query.count()}")
    if courses_query.exists():
        print(f"Courses for instructors: {[course.title for course in courses_query]}")
    else:
        print("No courses found for instructors.")

    # Filter courses by title if a search query is provided
    if course_search_query:
        courses_query = courses_query.filter(
            Q(title__icontains=course_search_query)
        )
        print(f"Number of courses (after search '{course_search_query}'): {courses_query.count()}")
        if courses_query.exists():
            print(f"Courses after search: {[course.title for course in courses_query]}")
        else:
            print(f"No courses found after search '{course_search_query}'.")

    courses = courses_query.order_by('-created_at')

    # Prepare course data with additional metrics
    course_data = []
    for course in courses:
        # Total enrollment
        total_enrollment = Enrollment.objects.filter(course=course).count()

        # Watch time (sum of lesson durations for completed lessons)
        watch_time = LessonProgress.objects.filter(
            course=course,
            completed=True
        ).aggregate(total_watch_time=Sum('lesson__duration'))['total_watch_time'] or 0
        watch_time_seconds = watch_time.total_seconds() if watch_time else 0

        # Course rating (placeholder; replace with actual logic if available)
        course_rating = 4.5

        course_data.append({
            'course': course,
            'mentor_name': course.instructor.get_full_name(),
            'watch_time': int(watch_time_seconds),
            'total_enrollment': total_enrollment,
            'published_on': course.created_at,
            'rating': course_rating,
        })

    # --- Mentee Section ---
    mentee_data = []
    for mentor in mentors:
        total_mentees = Enrollment.objects.filter(course__instructor=mentor).values('user').distinct().count()
        avg_price = Course.objects.filter(instructor=mentor).aggregate(Avg('price'))['price__avg'] or 0
        mentor_rating = 4.3  # Placeholder; replace with actual logic if available

        # Filter mentors by name if a search query is provided
        if mentee_search_query:
            if not (mentee_search_query.lower() in mentor.get_full_name().lower()):
                continue

        mentee_data.append({
            'mentor': mentor,
            'total_mentees': total_mentees,
            'price': int(avg_price),
            'rating': mentor_rating,
        })

    context = {
        'course_data': course_data,
        'mentee_data': mentee_data,
        'course_search_query': course_search_query,
        'mentee_search_query': mentee_search_query,
    }
    print(f"Course data length: {len(course_data)}")
    print(f"Mentee data length: {len(mentee_data)}")
    return render(request, 'mentor_user.html', context)

@login_required
def mentor_course_details_view(request, course_id):
    """
    View for Mentor Course Details.
    Displays detailed information about a specific course.
    """
    if not request.user.is_staff:
        return render(request, '403.html', status=403)

    course = get_object_or_404(Course, id=course_id)
    return render(request, 'mentor_course_details.html', {'course': course})

@login_required
def project_moderation_view(request):
    projects = Project.objects.all()
    return render(request, 'project_moderation.html', {'projects': projects})

@require_POST
@login_required
def remove_projects(request):
    selected_ids = request.POST.getlist('selected_ids')
    if selected_ids:
        Project.objects.filter(id__in=selected_ids).delete()
        messages.success(request, f"{len(selected_ids)} project(s) removed.")
    else:
        messages.warning(request, "No project selected.")
    return redirect('project_moderation') 

@login_required
def content_moderation_view(request):
    category = request.GET.get('category')
    if category:
        contents = Post.objects.filter(content_type=category.lower())
    else:
        contents = Post.objects.all()

    return render(request, 'content_moderation.html',{'contents': contents})

@require_POST
@login_required
def remove_posts(request):
    selected_ids = request.POST.getlist('selected_ids')
    if selected_ids:
        Post.objects.filter(id__in=selected_ids).delete()
        messages.success(request, f"{len(selected_ids)} post(s) removed.")
    else:
        messages.warning(request, "No content selected for removal.")
    return redirect('content_moderation')

@login_required
def service_desk_add_view(request):
    return render(request, 'service_desk_add.html')




# admin_login_view
def admin_login(request):
    return render(request, 'admin_login.html')

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views import View
class AdminLoginView(View):
    template_name = 'admin_login.html'
    
    def get(self, request):
        if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
            return redirect('admin_dashboard')
        return render(request, self.template_name)
    
    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            if user.is_staff or user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                messages.error(request, "This login is for admin and staff only.")
        else:
            messages.error(request, "Invalid username or password.")
        
        return render(request, self.template_name)
    

