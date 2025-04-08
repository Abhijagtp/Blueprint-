from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def dashboard_view(request):
    return render(request, 'admin_dashboard.html')

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