from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from Users.models import CustomUser
from django.contrib.auth import get_user_model
from django.utils.timezone import now
from django.db.models.functions import TruncMonth
from datetime import datetime, timedelta
import calendar
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

    prev_month = selected_month - 1 or 12
    prev_year = selected_year - 1 if prev_month == 12 else selected_year
    start_prev = datetime(prev_year, prev_month, 1)
    _, last_day_prev = calendar.monthrange(prev_year, prev_month)
    end_prev = datetime(prev_year, prev_month, last_day_prev, 23, 59, 59)

    current_month_users = CustomUser.objects.filter(date_joined__range=(start_selected, end_selected)).count()
    previous_month_users = CustomUser.objects.filter(date_joined__range=(start_prev, end_prev)).count()

    if previous_month_users == 0:
        percent_change = 100
    else:
        percent_change = ((current_month_users - previous_month_users) / previous_month_users) * 100

    selected_month = int(request.GET.get('month', datetime.now().month))
    
    months = [{'value': i, 'label': calendar.month_name[i]} for i in range(1, 13)]
    selected_month_label = calendar.month_name[selected_month]

    context = {
        'current_month_users': current_month_users,
        'percent_change': round(percent_change, 1),
        'percent_change_abs': abs(round(percent_change, 1)),
        'selected_month': selected_month,
        'selected_month_label': selected_month_label,
        'months': months,
    }

    return render(request, 'admin_dashboard.html', context)

@login_required
def analytics_view(request):
    return render(request, 'analytics.html')

@login_required
def user_management_view(request):
    return render(request, 'user_management.html')

@login_required
def organization_view(request):
    return render(request, 'organization_user.html') 

@login_required
def mentor_user_view(request):
    return render(request, 'mentor_user.html')

@login_required
def project_moderation_view(request):
    return render(request, 'project_moderation.html')

@login_required
def content_moderation_view(request):
    return render(request, 'content_moderation.html')