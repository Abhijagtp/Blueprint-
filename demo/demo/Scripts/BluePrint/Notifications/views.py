from django.shortcuts import render

# Create your views here.



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ActivityLog

@login_required
def notifications_page(request):
    # Get the filter type from the query parameters
    activity_type = request.GET.get('type', '')

    # Fetch activities for the logged-in user
    activities = ActivityLog.objects.filter(user=request.user).order_by('-timestamp')

    # Apply filter if a type is selected
    if activity_type:
        activities = activities.filter(activity_type=activity_type)

    context = {
        'activities': activities,
    }
    return render(request, 'notifications.html', context)

@login_required
def get_notification_count(request):
    unseen_count = ActivityLog.objects.filter(user=request.user, seen=False).count()
    return JsonResponse({'unseen_count': unseen_count})

@login_required
def mark_activity_as_seen(request, activity_id):
    activity = get_object_or_404(ActivityLog, id=activity_id, user=request.user)
    activity.seen = True
    activity.save()
    return JsonResponse({'success': True})