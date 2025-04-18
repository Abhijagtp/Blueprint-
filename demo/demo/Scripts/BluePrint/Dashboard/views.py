# from django.shortcuts import render

# from django.http import HttpResponse
# # Create your views here.
# # In dashboard/views.py
# from django.shortcuts import render


# def email_view(request):
#     return render(request,"inbox.html")


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# from .models import Email, CustomUser
# import json
# from django.db.models import Q
# from functools import reduce


# from django.http import JsonResponse
# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required
# import json

# @csrf_exempt
# @login_required
# def compose(request):
#     # Composing a new email must be via POST
#     if request.method != "POST":
#         return JsonResponse({"error": "POST request required."}, status=400)

#     # For file uploads, data is sent as multipart/form-data, so use request.POST and request.FILES
#     recipients_str = request.POST.get("recipients", "")
#     emails = [email.strip() for email in recipients_str.split(",")]
#     if emails == [""]:
#         return JsonResponse({"error": "At least one recipient required."}, status=400)

#     # Convert email addresses to user objects
#     recipients = []
#     for email in emails:
#         try:
#             user = CustomUser.objects.get(email=email)
#             recipients.append(user)
#         except CustomUser.DoesNotExist:
#             return JsonResponse({"error": f"User with email {email} does not exist."}, status=400)

#     # Get the other contents of the email
#     subject = request.POST.get("subject", "")
#     body = request.POST.get("body", "")

#     # Get the attachment from request.FILES; it will be None if no file was uploaded.
#     attachment = request.FILES.get("attachment")

#     # Create one email for each recipient plus the sender
#     users = set()
#     users.add(request.user)
#     users.update(recipients)
#     for user in users:
#         email_obj = Email(
#             user=user,
#             sender=request.user,
#             subject=subject,
#             body=body,  # Will be encrypted on save()
#             attachment=attachment,
#             read=(user == request.user)
#         )
#         email_obj.save()

#         # Add recipients for this email
#         for recipient in recipients:
#             email_obj.recipients.add(recipient)
#         email_obj.save()

#     return JsonResponse({"message": "Email sent successfully."}, status=201)


# @login_required
# def mailbox(request, mailbox):

#     # Filter emails returned based on mailbox
#     if mailbox == "inbox":
#         emails = Email.objects.filter(
#             user=request.user, recipients=request.user, archived=False, deleted=False,
#         )
#     elif mailbox == "sent":
#         emails = Email.objects.filter(
#             user=request.user, sender=request.user, deleted=False,
#         )
#     elif mailbox == "archive":
#         emails = Email.objects.filter(
#             user=request.user, archived=True, deleted=False,
#         ).filter( Q(sender=request.user) |Q(recipients=request.user))
#     elif mailbox == "starred":
#         emails = Email.objects.filter(
#             user=request.user, starred=True, deleted=False,
#         ).filter( Q(sender=request.user) |Q(recipients=request.user))
#     elif mailbox == "trash":
#         emails = Email.objects.filter(
#             user=request.user, deleted=True
#         ).filter( Q(sender=request.user) |Q(recipients=request.user))
    
#     else:
#         return JsonResponse({"error": "Invalid mailbox."}, status=400)

#     # Return emails in reverse chronologial order
#     emails = emails.order_by("-timestamp").all()
#     return JsonResponse([email.serialize() for email in emails], safe=False)









# @csrf_exempt
# @login_required
# def email(request, email_id):

#     # Query for requested email
#     try:
#         email = Email.objects.get(user=request.user, pk=email_id)
#     except Email.DoesNotExist:
#         return JsonResponse({"error": "Email not found."}, status=404)

#     # Return email contents
#     if request.method == "GET":
#         return JsonResponse(email.serialize())

#     # Update whether email is read or should be archived
#     elif request.method == "PUT":
#         data = json.loads(request.body)
#         if data.get("read") is not None:
#             email.read = data["read"]
#         if data.get("archived") is not None:
#             email.archived = data["archived"]
#         if data.get("starred") is not None:
#             email.starred = data["starred"]
#         if data.get("deleted") is not None:
#             email.deleted = data["deleted"]
#         email.save()
#         return HttpResponse(status=204)

#     elif request.method == "DELETE":
#         email.delete()
#         return HttpResponse(status=204)
#     # Email must be via GET or PUT
#     else:
#         return JsonResponse({
#             "error": "GET or PUT or DELETE request required."
#         }, status=400)


# from django.views.decorators.csrf import csrf_exempt
# from django.contrib.auth.decorators import login_required


# @csrf_exempt
# @login_required
# def search(request, query):
#     if " " in query:
#         queries = query.split(" ")
#         qset1 =  reduce(operator.__or__, [Q(sender__email__icontains=query) | Q(sender__first_name__icontains=query) | Q(sender__last_name__icontains=query)  | Q(subject__icontains=query) | Q(body__icontains=query) for query in queries])
#         results = Email.objects.filter(user=request.user).filter(qset1).distinct()
#     else:
#         results = Email.objects.filter(user=request.user)\
#             .filter(Q(sender__email__icontains=query) 
#             | Q(sender__first_name__icontains=query) 
#             | Q(sender__last_name__icontains=query) 
#             | Q(subject__icontains=query) 
#             | Q(body__icontains=query)).distinct()
#     if results:
#         emails = results.order_by("-timestamp").all().distinct()
#         return JsonResponse([email.serialize() for email in emails], safe=False)
#     else:
#         return JsonResponse({"error": "No result Found"}, status=404)
    

from django.http import HttpResponse

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from  Users.models import Message


@login_required
def get_unread_messages(request):
    """Fetch unread messages dynamically"""
    unread_messages = Message.objects.filter(receiver=request.user, is_read=False).order_by('-timestamp')
    
    if unread_messages.exists():
        latest_message = unread_messages.first()
        latest_message_info = {
            "id": latest_message.id,
            "sender": latest_message.sender.first_name,
            "text": latest_message.content[:50]  # Short preview
        }
        return JsonResponse({"unread_messages": unread_messages.count(), "latest_message": latest_message_info})
    
    return JsonResponse({"unread_messages": 0, "latest_message": None})

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.auth import get_user_model
from .models import Email, Reply
from django.views.decorators.csrf import csrf_exempt

User = get_user_model()

@login_required
def inbox(request):
    """Return all emails (sent and received) in JSON format for AJAX, or render HTML."""
    emails = Email.objects.filter(user=request.user, deleted=False).order_by('-timestamp')
    unread_count = emails.exclude(sender=request.user).filter(read=False, archived=False).count()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse([email.serialize() for email in emails], safe=False)
    return render(request, 'email.html', {'emails': emails, 'unread_count': unread_count})

@login_required
def sent_emails(request):
    """Return sent emails in JSON format."""
    emails = Email.objects.filter(sender=request.user, deleted=False, archived=False).order_by('-timestamp')
    return JsonResponse([email.serialize() for email in emails], safe=False)

@login_required
def archive_emails(request):
    """Return archived emails in JSON format."""
    emails = Email.objects.filter(user=request.user, archived=True, deleted=False).order_by('-timestamp')
    return JsonResponse([email.serialize() for email in emails], safe=False)

@login_required
def starred_emails(request):
    """Return starred emails in JSON format."""
    emails = Email.objects.filter(user=request.user, starred=True, deleted=False, archived=False).order_by('-timestamp')
    return JsonResponse([email.serialize() for email in emails], safe=False)

@login_required
def unread_emails(request):
    """Return unread emails in JSON format."""
    emails = Email.objects.filter(user=request.user, read=False, deleted=False, archived=False).order_by('-timestamp')
    return JsonResponse([email.serialize() for email in emails], safe=False)

@login_required
@require_POST
def archive_email(request, email_id):
    """Archive an email."""
    try:
        email = get_object_or_404(Email, id=email_id, user=request.user)
        email.archived = True
        email.save()
        return JsonResponse({'status': 'success', 'message': 'Email archived successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def unarchive_email(request, email_id):
    """Unarchive an email."""
    try:
        email = get_object_or_404(Email, id=email_id, user=request.user)
        email.archived = False
        email.save()
        return JsonResponse({'status': 'success', 'message': 'Email unarchived successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def star_email(request, email_id):
    """Star or unstar an email."""
    try:
        email = get_object_or_404(Email, id=email_id, user=request.user)
        import json
        data = json.loads(request.body or '{}')
        email.starred = not email.starred if data.get('action') == 'toggle' else True
        email.save()
        return JsonResponse({'status': 'success', 'message': 'Email star status updated successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def mark_as_read(request, email_id):
    """Mark an email as read."""
    try:
        email = get_object_or_404(Email, id=email_id, user=request.user)
        email.read = True
        email.save()
        return JsonResponse({'status': 'success', 'message': 'Email marked as read'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def mark_as_unread(request, email_id):
    """Mark an email as unread."""
    try:
        email = get_object_or_404(Email, id=email_id, user=request.user)
        email.read = False
        email.save()
        return JsonResponse({'status': 'success', 'message': 'Email marked as unread'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
@require_POST
def delete_email(request, email_id):
    """Mark an email as deleted."""
    try:
        email = get_object_or_404(Email, id=email_id, user=request.user)
        email.deleted = True
        email.save()
        return JsonResponse({'status': 'success', 'message': 'Email deleted successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def get_email(request, email_id):
    """Return email details in JSON format."""
    email = get_object_or_404(Email, id=email_id)
    if request.user != email.sender and request.user != email.user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    email.read = True
    email.save()
    return JsonResponse(email.serialize())

@login_required
def get_replies(request, email_id):
    """Return replies for a specific email."""
    email = get_object_or_404(Email, id=email_id)
    if request.user != email.sender and request.user != email.user:
        return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)
    replies = email.replies.all().order_by('timestamp')
    return JsonResponse([reply.serialize() for reply in replies], safe=False)

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
from .models import Email, Reply, Attachment
from Users.models import CustomUser

@login_required
@require_POST
def send_email(request):
    """Handle sending a new email with multiple attachments using usernames."""
    try:
        data = request.POST
        recipient_username = data.get('recipient')
        subject = data.get('subject')
        body = data.get('body')
        attachments = request.FILES.getlist('attachments')

        # Look up the recipient by username
        recipient = get_object_or_404(CustomUser, username=recipient_username)

        # Validate total attachment size
        total_size = sum(file.size for file in attachments)
        if total_size > 100 * 1024 * 1024:  # 100MB limit
            return JsonResponse({'status': 'error', 'message': 'Total attachment size exceeds 100MB'}, status=400)

        # Create email for the sender
        sender_email = Email(
            user=request.user,
            sender=request.user,
            subject=subject,
            body=body,
        )
        sender_email.save()
        sender_email.recipients.add(recipient)

        # Create email for the recipient
        recipient_email = Email(
            user=recipient,
            sender=request.user,
            subject=subject,
            body=body,
            read=False,
        )
        recipient_email.save()
        recipient_email.recipients.add(recipient)

        # Save attachments for both sender and recipient emails
        for attachment in attachments:
            Attachment.objects.create(email=sender_email, file=attachment)
            Attachment.objects.create(email=recipient_email, file=attachment)

        return JsonResponse({'status': 'success', 'message': 'Email sent successfully'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Recipient username does not exist'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@login_required
@require_POST
def reply_email(request):
    """Handle replying to an email with multiple attachments using usernames."""
    try:
        data = request.POST
        email_id = data.get('email_id')
        body = data.get('reply_body')
        recipient_username = data.get('recipient')
        attachments = request.FILES.getlist('attachments')

        # Look up the email and recipient
        email = get_object_or_404(Email, id=email_id)
        recipient = get_object_or_404(CustomUser, username=recipient_username)

        # Authorization check
        if request.user != email.sender and request.user != email.user:
            return JsonResponse({'status': 'error', 'message': 'Unauthorized'}, status=403)

        # Validate total attachment size
        total_size = sum(file.size for file in attachments)
        if total_size > 100 * 1024 * 1024:  # 100MB limit
            return JsonResponse({'status': 'error', 'message': 'Total attachment size exceeds 100MB'}, status=400)

        # Create the reply
        reply = Reply(
            email=email,
            sender=request.user,
            body=body,
        )
        reply.save()

        # Save attachments for the reply
        for attachment in attachments:
            Attachment.objects.create(reply=reply, file=attachment)

        return JsonResponse({'status': 'success', 'message': 'Reply sent successfully'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Recipient username does not exist'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    


# views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from datetime import timedelta, datetime
from django.utils import timezone
from .models import CustomUser
from Users.models import UserProfile, Education, Experience, Message, FollowRequest, Post
from Training.models import Enrollment, LessonProgress
from WorkListing.models import ProjectRequest


@login_required
def dashboard(request):
    user = request.user
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = None

    if not user_profile:
        return render(request, 'dashboard_new.html', {'error': 'User profile not found'})

    # Timeline data (Education and Experience)
    educations = Education.objects.filter(user_profile=user_profile).order_by('start_date')
    experiences = Experience.objects.filter(user_profile=user_profile).order_by('from_date')

    # Impressions (from posts)
    # Define time periods
    now = timezone.now()
    current_period_start = now - timedelta(days=30)  # Last 30 days
    previous_period_start = now - timedelta(days=60)  # 60 to 30 days ago
    previous_period_end = current_period_start

    # Current period impressions (last 30 days)
    current_posts = Post.objects.filter(
        user_profile=user_profile,
        created_at__gte=current_period_start,
        created_at__lte=now
    )
    total_impressions_current = current_posts.aggregate(total=Count('likes'))['total'] or 0
    avg_daily_impressions = total_impressions_current / 30  # Average over 30 days

    # Previous period impressions (60 to 30 days ago)
    previous_posts = Post.objects.filter(
        user_profile=user_profile,
        created_at__gte=previous_period_start,
        created_at__lt=previous_period_end
    )
    total_impressions_previous = previous_posts.aggregate(total=Count('likes'))['total'] or 0
    avg_daily_impressions_previous = total_impressions_previous / 30  # Average over 30 days

    # Calculate percentage change
    if avg_daily_impressions_previous > 0:
        avg_daily_impressions_change = (
            (avg_daily_impressions - avg_daily_impressions_previous) / avg_daily_impressions_previous * 100
        )
    else:
        avg_daily_impressions_change = 100 if avg_daily_impressions > 0 else 0  # If previous is 0, set to 100% if current is non-zero

    # Round the values for display
    avg_daily_impressions = round(avg_daily_impressions, 2)
    avg_daily_impressions_change = round(avg_daily_impressions_change, 2)

    # Total impressions (for display, can be over all time)
    posts = Post.objects.filter(user_profile=user_profile)
    total_impressions = posts.aggregate(total=Count('likes'))['total'] or 0

    # Courses taken
    enrollments = Enrollment.objects.filter(user=user, is_active=True)
    total_courses = enrollments.count()
    completed_courses = LessonProgress.objects.filter(user=user, completed=True).values('course').distinct().count()

    # Calculate percentage change for completed courses
    # For simplicity, assume we track completed courses over the same periods
    completed_courses_current = LessonProgress.objects.filter(
        user=user,
        completed=True,
        updated_at__gte=current_period_start,
        updated_at__lte=now
    ).values('course').distinct().count()

    completed_courses_previous = LessonProgress.objects.filter(
        user=user,
        completed=True,
        updated_at__gte=previous_period_start,
        updated_at__lt=previous_period_end
    ).values('course').distinct().count()

    if completed_courses_previous > 0:
        completed_courses_change = (
            (completed_courses_current - completed_courses_previous) / completed_courses_previous * 100
        )
    else:
        completed_courses_change = 100 if completed_courses_current > 0 else 0

    completed_courses_change = round(completed_courses_change, 2)

    # Project status
    project_requests = ProjectRequest.objects.filter(professional=user)
    pending_projects = project_requests.filter(status='pending').count()
    accepted_projects = project_requests.filter(status='accepted').count()
    total_projects = project_requests.count() or 1  # Avoid division by zero
    # Calculate the percentage of accepted projects
    project_percentage = (accepted_projects / total_projects * 100) if total_projects > 0 else 0
    project_deadline = project_requests.filter(status='accepted').order_by('project__submission_date').first()

    # Conversations (Messages)
    conversations = Message.objects.filter(receiver=user, is_read=False).order_by('-timestamp')[:2]

    # Time spent learning
    lesson_progress = LessonProgress.objects.filter(user=user, updated_at__gte=timezone.now() - timedelta(days=7))
    total_time_spent = lesson_progress.count() * 10  # Assuming 10 minutes per lesson for simplicity
    time_spent_hours = total_time_spent // 60
    time_spent_minutes = total_time_spent % 60

    # Activity breakdown (Certifications, Whitepapers, Blogs, Projects)
    certifications = user_profile.certifications.count()
    try:
        whitepapers = user_profile.whitepapers.count()
    except AttributeError:
        whitepapers = 0  # Fallback in case the relationship isn't set
    blogs = user_profile.blogs.count()
    projects = user_profile.projects.count()

    # Followed pages
    followed_users = FollowRequest.objects.filter(from_user=user, status='accepted').select_related('to_user')

    context = {
        'user': user,  # Added for the template
        'educations': educations,
        'experiences': experiences,
        'total_impressions': total_impressions,
        'avg_daily_impressions': avg_daily_impressions,
        'avg_daily_impressions_change': avg_daily_impressions_change,  # Added
        'total_courses': total_courses,
        'completed_courses': completed_courses,
        'completed_courses_change': completed_courses_change,  # Added
        'pending_projects': pending_projects,
        'accepted_projects': accepted_projects,
        'total_projects': total_projects,
        'project_percentage': project_percentage,
        'project_deadline': project_deadline,
        'conversations': conversations,
        'time_spent_hours': time_spent_hours,
        'time_spent_minutes': time_spent_minutes,
        'certifications': certifications,
        'whitepapers': whitepapers,
        'blogs': blogs,
        'projects': projects,
        'followed_users': followed_users,
    }
    return render(request, 'dashboard_new.html', context)