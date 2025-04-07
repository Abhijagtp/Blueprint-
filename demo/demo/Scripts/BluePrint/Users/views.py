from django.shortcuts import render

# Create your views here.


def home(request):
    return render(request,'home.html')


def user_selection(request):
    return render(request,'user_selection.html')


from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model

User = get_user_model()

def user_type_selection_view(request):
    if request.method == "POST":
        # Get selected user type
        user_type = request.POST.get("user_type")

        # Store user type in session to use in the registration process
        request.session['user_type'] = user_type

        return redirect('register')  # Redirect to registration page after user type selection
    return render(request, "user_type_selection.html")




from django.shortcuts import render, redirect
from django.contrib.auth import login, get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.urls import reverse

User = get_user_model()

def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        first_name = request.POST.get("fname")
        last_name = request.POST.get("lname")
        password = request.POST.get("password")
        confirmation = request.POST.get("confirmation")
        user_type = request.session.get("user_type", "professional")  # Get the user type from the session

        # Ensure passwords match
        if password != confirmation:
            return render(request, "register.html", {"message": "Passwords must match."})

        try:
            # Validate the password
            validate_password(password)

            # Attempt to create the user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type=user_type,  # Set the user type
            )
            user.save()

            # Log in the user
           

            # Redirect to the login page
            return redirect('login')

        except ValidationError as e:
            return render(request, "register.html", {"message": e.messages[0]})
        except Exception as e:
            return render(request, "register.html", {"message": "An unexpected error occurred. Please try again."})
    else:
        return render(request, "register.html")


from django.shortcuts import render, HttpResponseRedirect
from django.contrib.auth import authenticate, login
from django.urls import reverse

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import CustomUser, Organization, User_form  # Import User_form model

def login_view(request):
    if request.user.is_authenticated:
        # Check user type and redirect accordingly
        if request.user.user_type == CustomUser.ORGANIZATIONAL:
            try:
                # Check if organization profile exists
                Organization.objects.get(user=request.user)
                return redirect('dashboard_new')
            except Organization.DoesNotExist:
                return redirect('org_form')
        elif request.user.user_type == CustomUser.PROFESSIONAL:
            try:
                # Check if professional profile exists
                User_form.objects.get(user=request.user)
                return redirect('dashboard_new')
            except User_form.DoesNotExist:
                return redirect('user_form')
        return redirect('dashboard_new')

    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            # Check user type and redirect accordingly
            if user.user_type == CustomUser.ORGANIZATIONAL:
                try:
                    Organization.objects.get(user=user)
                    return redirect('dashboard_new')
                except Organization.DoesNotExist:
                    return redirect('org_form')
            elif user.user_type == CustomUser.PROFESSIONAL:
                try:
                    User_form.objects.get(user=user)
                    return redirect('dashboard_new')
                except User_form.DoesNotExist:
                    return redirect('user_form')
            return redirect('dashboard_new')
        else:
            return render(request, "login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "login.html")
    
from django.shortcuts import render
from django.contrib.auth import logout
def logout_view(request):
    logout(request)
    return redirect('login') 


    

# myapp/views.py
from django.shortcuts import render, redirect
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.contrib import messages
import random
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            # Generate 6-digit OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            # Store OTP in session
            request.session['otp'] = otp
            request.session['email'] = email
            # Email content
            subject = 'BluePrint: Reset Your Password'
            html_message = render_to_string('otp_email.html', {
                'username': user.username,
                'otp': otp,
                'year': 2025  # For footer
            })
            plain_message = strip_tags(html_message)  # Fallback for non-HTML clients
            from_email = 'BluePrint <noreply@yourwebsite.com>'  # Update with your email
            send_mail(subject, plain_message, from_email, [email], html_message=html_message)
            messages.success(request, 'OTP has been sent to your email.')
            return redirect('verify_otp')
        except User.DoesNotExist:
            messages.error(request, 'No user found with this email.')
    return render(request, 'forgot_password.html')

def verify_otp(request):
    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('otp')
        if entered_otp == stored_otp:
            messages.success(request, 'OTP verified successfully.')
            return redirect('set_new_password')
        else:
            messages.error(request, 'Invalid OTP. Please try again.')
    return render(request, 'verify_otp.html')

def set_new_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        email = request.session.get('email')
        if password == confirm_password:
            try:
                user = User.objects.get(email=email)
                user.set_password(password)
                user.save()
                # Clear session data
                del request.session['otp']
                del request.session['email']
                messages.success(request, 'Password reset successfully. Please login.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Something went wrong.')
        else:
            messages.error(request, 'Passwords do not match.')
    return render(request, 'set_new_password.html')


import yfinance as yf
from django.http import JsonResponse

def fetch_nifty_sensex_data():
    indices = {
        'Nifty 50': '^NSEI',
        'Sensex': '^BSESN',
    }
    market_data = []
    
    for name, symbol in indices.items():
        stock = yf.Ticker(symbol)
        data = stock.history(period='5d')  # Get the last 5 days of data
        
        if not data.empty:
            # Extract the necessary data: dates, high, low, open, and closing prices
            dates = data.index.strftime('%Y-%m-%d').tolist()
            highs = data['High'].tolist()
            lows = data['Low'].tolist()
            opens = data['Open'].tolist()
            closing_prices = data['Close'].tolist()
            
            # Latest data for general information
            latest_data = data.iloc[-1]
            change_percent = ((latest_data['Close'] - latest_data['Open']) / latest_data['Open']) * 100
            
            market_data.append({
                'name': name,
                'symbol': symbol,
                'high': round(latest_data['High'], 2),
                'low': round(latest_data['Low'], 2),
                'open': round(latest_data['Open'], 2),
                'close': round(latest_data['Close'], 2),
                'change_percent': round(change_percent, 2),
                'dates': dates,
                'highs': [round(h, 2) for h in highs],
                'lows': [round(l, 2) for l in lows],
                'opens': [round(o, 2) for o in opens],
                'closing_prices': [round(c, 2) for c in closing_prices]
            })
    
    return market_data

def fetch_sector_performance(request):
    sectors = {
        'Technology': '^CNXIT',
        'Energy': '^CNXENERGY',
        'Pharma': '^CNXPHARMA',
        'Auto': '^CNXAUTO',
    }
    sector_data = []
    for name, symbol in sectors.items():
        stock = yf.Ticker(symbol)
        data = stock.history(period='1d')
        if not data.empty:
            latest_data = data.iloc[-1]
            open_price = round(latest_data['Open'], 2)
            close_price = round(latest_data['Close'], 2)
            change_percent = ((close_price - open_price) / open_price) * 100
            sector_data.append({
                'name': name,
                'open': open_price,
                'close': close_price,
                'change_percent': round(change_percent, 2)
            })
    
    return JsonResponse(sector_data, safe=False)

def market_data_view(request):
    market_data = fetch_nifty_sensex_data()
    return JsonResponse(market_data, safe=False)

from django.shortcuts import render



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import UserProfile



from django.db.models import Count

def profile_view(request, username=None):
    """
    If a username is provided in the URL, load that user’s profile.
    Otherwise, load the logged-in user’s profile.
    """
    if username:
        # Viewing someone else's profile
        user_obj = get_object_or_404(CustomUser, username=username)
        user_profile, created = UserProfile.objects.get_or_create(user=user_obj)
        is_owner = (user_obj == request.user)
    else:
        # Viewing own profile
        user_obj = request.user
        user_profile, created = UserProfile.objects.get_or_create(user=request.user)
        is_owner = True

    # Follow request logic
    follow_request_status = None
    if FollowRequest.objects.filter(from_user=request.user, to_user=user_obj, status='accepted').exists() or \
       FollowRequest.objects.filter(from_user=user_obj, to_user=request.user, status='accepted').exists():
        follow_request_status = 'accepted'
    elif FollowRequest.objects.filter(from_user=request.user, to_user=user_obj, status='pending').exists():
        follow_request_status = 'pending'

    # Get counts for followers, following, and posts
    followers_count = FollowRequest.objects.filter(to_user=user_obj, status='accepted').count()
    following_count = FollowRequest.objects.filter(from_user=user_obj, status='accepted').count()
    posts_count = Post.objects.filter(user_profile=user_profile).count()

    # If an AJAX request is sent (for experiences, etc.)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        experiences = Experience.objects.filter(user_profile=user_profile).values(
            'title', 'organization_name', 'is_current', 'from_date', 'to_date', 'skills_gained'
        )
        return JsonResponse(list(experiences), safe=False)

    context = {
        'user_obj': user_obj,
        'user_profile': user_profile,
        'is_owner': is_owner,  # Flag to decide which buttons to show in the template
        'follow_request_status': follow_request_status,  # Status of follow request
        'experiences': Experience.objects.filter(user_profile=user_profile),
        'educations': Education.objects.filter(user_profile=user_profile),
        'skills': Skill.objects.filter(user_profile=user_profile),
        'first_name': user_obj.first_name,
        'last_name': user_obj.last_name,
        'bio': user_profile.bio if user_profile else '',
        'followers_count': followers_count,  # Number of followers
        'following_count': following_count,  # Number of users being followed
        'posts_count': posts_count,  # Number of posts
    }
    return render(request, 'profile.html', context)








from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import UserProfile, Experience, Education, Skill


import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from .models import UserProfile, Experience, Education, Skill

@csrf_exempt
@login_required
def save_profile(request):
    if request.method == "POST":
        data = json.loads(request.body)
        
        # Update User Model
        request.user.first_name = data.get("fname", request.user.first_name)
        request.user.last_name = data.get("lname", request.user.last_name)
        request.user.save()

        # Update or create UserProfile
        user_profile, _ = UserProfile.objects.update_or_create(
            user=request.user,
            defaults={"bio": data.get("bio"), "website": data.get("website")}
        )
        
        return JsonResponse({"status": "success", "profile_id": user_profile.id})
    
    return JsonResponse({"status": "error"}, status=400)



# views.py
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def update_profile_image(request):
    if request.method == "POST":
        profile = request.user.userprofile
        if 'profile_image' in request.FILES:
            profile.profile_image = request.FILES['profile_image']
            profile.save()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)

@login_required
def update_cover_image(request):
    if request.method == "POST":
        profile = request.user.userprofile
        if 'cover_image' in request.FILES:
            profile.cover_image = request.FILES['cover_image']
            profile.save()
            return JsonResponse({"status": "success"})
    return JsonResponse({"status": "error"}, status=400)



from django.shortcuts import render
from django.http import JsonResponse

def load_tab_content(request):
    section = request.GET.get('section', 'posts')  # Default to 'posts' if no section is provided
    username = request.GET.get('username', '')

    # Render the appropriate template based on the section
    if section == 'posts':
        return load_posts(request)
    elif section == 'experience':
        return load_experience(request)
    elif section == 'education':
        return load_education(request)
    elif section == 'skills':
        return load_skills(request)
    elif section == 'projects':
        return load_projects(request)
    elif section == 'certifications':
        return load_certifications(request)
    else:
        return JsonResponse({'error': 'Invalid section'}, status=400)
    


from django.shortcuts import render
from django.http import JsonResponse

def load_posts_content(request):
    section = request.GET.get('section', 'blogs')  # Default to 'blogs' if no section is provided

    # Render the appropriate template based on the section
    if section == 'blogs':
        return render(request, 'tabs/blogs.html')
    elif section == 'whitepapers':
        return render(request, 'tabs/whitepapers.html')
    else:
        return JsonResponse({'error': 'Invalid section'}, status=400)
    


# experience



from django.shortcuts import render
from .models import Experience, Education, Skill,Certification,Project



from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def load_experience(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({"error": "Username is required"}, status=400)

    user_obj = get_object_or_404(CustomUser, username=username)
    user_profile = get_object_or_404(UserProfile, user=user_obj)

    experiences = Experience.objects.filter(user_profile=user_profile)
    is_owner = request.user == user_obj  # Check if the logged-in user is the profile owner

    return render(request, 'tabs/experience.html', {
        'experiences': experiences,
        'is_owner': is_owner
    })


@login_required
def load_education(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({"error": "Username is required"}, status=400)

    user_obj = get_object_or_404(CustomUser, username=username)
    user_profile = get_object_or_404(UserProfile, user=user_obj)

    educations = Education.objects.filter(user_profile=user_profile)
    is_owner = request.user == user_obj  

    return render(request, 'tabs/education.html', {
        'educations': educations,
        'is_owner': is_owner
    })


@login_required
def load_skills(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({"error": "Username is required"}, status=400)

    user_obj = get_object_or_404(CustomUser, username=username)
    user_profile = get_object_or_404(UserProfile, user=user_obj)

    skills = Skill.objects.filter(user_profile=user_profile)
    is_owner = request.user == user_obj  

    return render(request, 'tabs/skills.html', {
        'skills': skills,
        'is_owner': is_owner
    })


@login_required
def load_certifications(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({"error": "Username is required"}, status=400)

    user_obj = get_object_or_404(CustomUser, username=username)
    user_profile = get_object_or_404(UserProfile, user=user_obj)

    certifications = Certification.objects.filter(user_profile=user_profile)
    is_owner = request.user == user_obj  

    return render(request, 'tabs/certifications.html', {
        'certifications': certifications,
        'is_owner': is_owner
    })


@login_required
def load_projects(request):
    username = request.GET.get('username')
    if not username:
        return JsonResponse({"error": "Username is required"}, status=400)

    user_obj = get_object_or_404(CustomUser, username=username)
    user_profile = get_object_or_404(UserProfile, user=user_obj)

    projects = Project.objects.filter(user_profile=user_profile)
    is_owner = request.user == user_obj  

    return render(request, 'tabs/projects.html', {
        'projects': projects,
        'is_owner': is_owner
    })




from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Post  # Assuming your Post model is here
from Users.models import CustomUser, UserProfile

def load_posts(request):
    username = request.GET.get('username')  # Get username from request
    if not username:
        return JsonResponse({"error": "Username is required"}, status=400)

    user_obj = get_object_or_404(CustomUser, username=username)  # Get user object
    user_profile = get_object_or_404(UserProfile, user=user_obj)  # Get user profile

    # Fetch only posts belonging to the viewed profile
    posts = Post.objects.filter(user_profile=user_profile).order_by('-created_at')



    return render(request, 'tabs/posts.html', {'posts': posts})






import json
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Experience, UserProfile

def parse_date(date_str):
    if not date_str or date_str.strip() == "":
        return None
    try:
        # Try four-digit year first:
        return datetime.strptime(date_str, "%d-%m-%Y").date()
    except ValueError:
        # Then try two-digit year
        try:
            return datetime.strptime(date_str, "%d-%m-%y").date()
        except ValueError:
            return None

import json
from datetime import datetime
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import Experience, UserProfile

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Experience
from .forms import ExperienceForm

@login_required
def save_experience(request):
    if request.method == "POST":
        form = ExperienceForm(request.POST)
        
        if form.is_valid():
            experience = form.save(commit=False)
            experience.user_profile = request.user.userprofile  # Assign the logged-in user's profile
            experience.save()
            return redirect("profile")  # Redirect to the profile page after saving
        
        return render(request, "experience_form.html", {"form": form})

    return redirect("profile")  # Redirect if not a POST request




from django.shortcuts import render, get_object_or_404, redirect
from .models import Experience
from .forms import ExperienceForm

def edit_experience(request, experience_id):
    experience = get_object_or_404(Experience, id=experience_id)
    
    if request.method == "POST":
        form = ExperienceForm(request.POST, instance=experience)
        if form.is_valid():
            form.save()
            return redirect('profile')  # Redirect to experience list

    return redirect('profile')

def delete_experience(request, experience_id):
    experience = get_object_or_404(Experience, id=experience_id)
    
    if request.method == "POST":
        experience.delete()
        return redirect('profile')

    return redirect('profile')


# Education CRUD    
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Education
from .forms import EducationForm

@login_required
def education_list(request):
    educations = Education.objects.filter(user_profile=request.user.userprofile)
    form = EducationForm()
    return render(request, 'education.html', {'educations': educations, 'form': form})

@login_required
def add_education(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.user_profile = request.user.userprofile
            education.save()
            return redirect('profile')
    return redirect('profile')

@login_required
def edit_education(request, education_id):
    education = get_object_or_404(Education, id=education_id, user_profile=request.user.userprofile)
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=education)
        if form.is_valid():
            form.save()
            return redirect('profile')
    return redirect('profile')

@login_required
def delete_education(request, education_id):
    education = get_object_or_404(Education, id=education_id, user_profile=request.user.userprofile)
    if request.method == 'POST':
        education.delete()
    return redirect('profile')

# skills section 
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Skill
from .forms import SkillForm

@login_required
def add_skill(request):
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user_profile = request.user.userprofile
            skill.save()
            return redirect("profile")  # Redirect to profile page after adding
    return redirect("profile")

@login_required
def update_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user_profile=request.user.userprofile)
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            return redirect("profile")
    return redirect("profile")

@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user_profile=request.user.userprofile)
    skill.delete()
    return redirect("profile")
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Skill
from .forms import SkillForm

@login_required
def add_skill(request):
    if request.method == "POST":
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.user_profile = request.user.userprofile
            skill.save()
            return redirect("profile")  # Redirect to profile page after adding
    return redirect("profile")

@login_required
def update_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user_profile=request.user.userprofile)
    if request.method == "POST":
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            form.save()
            return redirect("profile")
    return redirect("profile")

@login_required
def delete_skill(request, skill_id):
    skill = get_object_or_404(Skill, id=skill_id, user_profile=request.user.userprofile)
    skill.delete()
    return redirect("profile")



from django.shortcuts import render, redirect
from .models import Certification, Skill
from .forms import CertificationForm
from django.contrib.auth.decorators import login_required

@login_required
def add_certification(request):
    if request.method == "POST":
        form = CertificationForm(request.POST, request.FILES)
        if form.is_valid():
            certification = form.save(commit=False)
            certification.user_profile = request.user.userprofile  # Associate with logged-in user
            certification.save()

            # Debugging: Print request data
            print("Received POST data:", request.POST)

            # Handle Skills Processing
            skills_text = form.cleaned_data.get('skills_gained', "").strip()
            if skills_text:
                skill_names = [skill.strip() for skill in skills_text.split(",")]  # Split by comma
                print("Extracted skills:", skill_names)  # Debugging

                for skill_name in skill_names:
                    if skill_name:
                        skill, created = Skill.objects.get_or_create(
                            user_profile=request.user.userprofile,
                            skill_name=skill_name
                        )
                        print(f"Skill '{skill_name}' - Created: {created}")  # Debugging
                        certification.skills_gained.add(skill)  # Associate skill with certification

            return redirect("profile")  # Redirect after successful save
        else:
            print("Form Errors:", form.errors)  # Debugging

    return redirect("profile")

from django.shortcuts import render, get_object_or_404, redirect
from .models import Certification

def edit_certification(request, cert_id):
    cert = get_object_or_404(Certification, id=cert_id)
    if request.method == "POST":
        cert.course_name = request.POST["course_name"]
        cert.issuing_organization = request.POST["issuing_organization"]
        cert.completion_date = request.POST["completion_date"]
        if request.FILES.get("certificate_file"):
            cert.certificate_file = request.FILES["certificate_file"]
        cert.save()
        return redirect("[profile]")  # Change to your actual redirect URL
    return redirect("profile")

def delete_certification(request, cert_id):
    cert = get_object_or_404(Certification, id=cert_id)
    if request.method == "POST":
        cert.delete()
        return redirect("profile")
    return redirect("profile")



from django.shortcuts import render, get_object_or_404, redirect
from .models import Project
from .forms import ProjectForm

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Project
from .forms import ProjectForm

@login_required
def add_project(request):
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.user_profile = request.user.userprofile  # Assign logged-in user's profile
            project.save()
            messages.success(request, "Project added successfully!")
        else:
            messages.error(request, "Error adding project. Please check the form.")
    return redirect('profile')

@login_required
def edit_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user_profile=request.user.userprofile)
    
    if request.method == "POST":
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.success(request, "Project updated successfully!")
        else:
            messages.error(request, "Error updating project. Please check the form.")
    
    return redirect('profile')

@login_required
def delete_project(request, project_id):
    project = get_object_or_404(Project, id=project_id, user_profile=request.user.userprofile)
    project.delete()
    messages.success(request, "Project deleted successfully!")
    return redirect('profile')



# =============================================================================================================================

    # Timeline Views 
# ===================================================================================================================================



# timeline 
from django.shortcuts import render
from .models import Post, FollowRequest
from DigitalAssets.models import Blog, Whitepaper, Insight



def timeline_view(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if not authenticated

    # Step 1: Check for any accepted follow connections involving the current user
    has_follow_connections = FollowRequest.objects.filter(
        models.Q(from_user=request.user) | models.Q(to_user=request.user),  # User is either follower or followee
        status='accepted'
    ).exists()

    # Step 2: Initialize post_data
    post_data = []

    # Step 3: Determine which posts to fetch
    if has_follow_connections:
        # If there are follow connections, get followers and followees
        incoming_followers = FollowRequest.objects.filter(
            to_user=request.user,  # Users who follow the current user
            status='accepted'
        ).values_list('from_user', flat=True)

        outgoing_follows = FollowRequest.objects.filter(
            from_user=request.user,  # Users the current user follows
            status='accepted'
        ).values_list('to_user', flat=True)

        # Combine followers, followees, and self into users_to_show
        users_to_show = set(incoming_followers) | set(outgoing_follows)  # Union of followers and followees
        users_to_show = list(users_to_show) + [request.user.id]  # Include current user's ID
    else:
        # If no follow connections, only include the current user's ID
        users_to_show = [request.user.id]

    # Step 4: Fetch posts based on users_to_show
    posts = Post.objects.filter(
        user_profile__user__id__in=users_to_show
    ).select_related('user_profile__user').prefetch_related('likes', 'comments').order_by('-created_at')

    # Step 5: Prepare post_data
    for post in posts:
        post_info = {
            'post': post,
            'content': None
        }
        if post.content_type == 'blog':
            try:
                post_info['content'] = Blog.objects.get(id=post.content_id)
            except Blog.DoesNotExist:
                post_info['content'] = None
        elif post.content_type == 'whitepaper':
            try:
                post_info['content'] = Whitepaper.objects.get(id=post.content_id)
            except Whitepaper.DoesNotExist:
                post_info['content'] = None
        elif post.content_type == 'insight':
            try:
                post_info['content'] = Insight.objects.get(id=post.content_id)
            except Insight.DoesNotExist:
                post_info['content'] = None
        post_data.append(post_info)

    # Step 6: Render the template with post_data
    return render(request, 'timeline.html', {'post_data': post_data})

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

@login_required
def get_follower_user_ids(request):
    follower_ids = FollowRequest.objects.filter(
        to_user=request.user,
        status='accepted'
    ).values_list('from_user_id', flat=True)
    return JsonResponse({'follower_user_ids': list(follower_ids)})

from django.contrib.auth.decorators import login_required
@login_required
def get_following_user_ids(request):
    print(f"User: {request.user}, Authenticated: {request.user.is_authenticated}")
    follower_user_ids = FollowRequest.objects.filter(
        to_user=request.user,  # Others follow the current user
        status='accepted'
    ).values_list('from_user_id', flat=True)
    follower_user_ids = list(follower_user_ids) + [request.user.id]
    print(f"Follower user IDs in endpoint: {follower_user_ids}")
    return JsonResponse({
        'following_user_ids': follower_user_ids
    })


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q

@login_required
def check_follow_connections(request):
    has_follow_connections = FollowRequest.objects.filter(
        Q(from_user=request.user) | Q(to_user=request.user),
        status='accepted'
    ).exists()
    return JsonResponse({'has_follow_connections': has_follow_connections})


from django.http import JsonResponse
from django.utils import timezone
from .models import Post

def get_new_posts(request):
    last_post_time = request.GET.get('last_post_time')
    if last_post_time:
        last_post_time = timezone.datetime.fromisoformat(last_post_time)
        new_posts = Post.objects.filter(created_at__gt=last_post_time).order_by('-created_at')
    else:
        new_posts = Post.objects.order_by('-created_at')[:10]  # Get the latest 10 posts

    posts_data = [{
        'id': post.id,
        'caption': post.caption,
        'image': post.image.url if post.image else None,
        'created_at': post.created_at.isoformat(),
        'user_profile_image': post.user_profile.profile_image.url if post.user_profile.profile_image else None,
        'username': post.user_profile.user.username,
        'full_name': post.user_profile.user.get_full_name(),
        'like_count': post.likes.count(),
        'comment_count': post.comments.count(),
    } for post in new_posts]

    return JsonResponse({'posts': posts_data})


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Post, UserProfile

@login_required
@require_POST
def create_post(request):
    try:
        # Get the caption and image from the request
        caption = request.POST.get("caption")
        image = request.FILES.get("image")

        # Validate the caption
        if not caption:
            return JsonResponse({'success': False, 'error': 'Caption is required'}, status=400)

        # Validate the image (if provided)
        if image:
            # Check file size (e.g., max 5MB)
            max_size = 5 * 1024 * 1024  # 5MB in bytes
            if image.size > max_size:
                return JsonResponse({'success': False, 'error': 'File size exceeds 5MB limit'}, status=400)

            # Check file type
            allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'video/mp4', 'video/webm']
            if image.content_type not in allowed_types:
                return JsonResponse({'success': False, 'error': 'Unsupported file type. Allowed types: JPEG, PNG, GIF, WebP, MP4, WebM'}, status=400)

        # Get or create the user profile
        try:
            user_profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            user_profile = UserProfile.objects.create(user=request.user)

        # Create the post
        post = Post.objects.create(
            user_profile=user_profile,
            caption=caption,
            image=image,
            content_type='normal'  # Explicitly set content_type to 'normal'
        )

        # Prepare post data for WebSocket broadcast
        post_data = {
            "id": str(post.id),
            "username": request.user.username,
            "full_name": request.user.get_full_name(),
            "user_id": str(request.user.id),
            "user_profile_image": user_profile.profile_image.url if user_profile.profile_image else "/static/images/Profile-default.png",
            "caption": post.caption,
            "image": post.image.url if post.image else None,
            "created_at": post.created_at.isoformat(),
            "like_count": 0,
            "comment_count": 0,
            "content_type": post.content_type,
        }

        # Broadcast the new post to all connected clients
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "timeline",
            {
                "type": "broadcast_post",
                "post": post_data,
            }
        )

        return JsonResponse({"success": True, "post": post_data})
    except ValidationError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': f'Server error: {str(e)}'}, status=500)

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Post

@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.user_profile.user == request.user:
        post.delete()
        messages.success(request, "Post deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this post.")
    return redirect("timeline")  # Adjust the redirect as needed

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import FollowRequest


@login_required
def get_followers(request):
    followers = FollowRequest.objects.filter(to_user=request.user, status="accepted").select_related("from_user")
    
    followers_data = [
        {
            "id": follower.from_user.id,
            "name": follower.from_user.get_full_name(),
            "profile_image": follower.from_user.userprofile.profile_image.url if follower.from_user.userprofile.profile_image else "/static/default-profile.png"
        }
        for follower in followers
    ]
    
    return JsonResponse({"followers": followers_data})


import logging
import re
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

# Set up logging
logger = logging.getLogger(__name__)

@login_required
def send_post_share(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            post_id = data.get("post_id")
            recipients = data.get("recipients", [])
            message = data.get("message", "").strip()

            if not post_id or not recipients:
                logger.error("Invalid request data: post_id or recipients missing")
                return JsonResponse({"error": "Invalid request data"}, status=400)

            logger.info(f"Sharing post {post_id} with recipients {recipients}")

            # Fetch the post
            post = Post.objects.get(id=post_id)
            sender = request.user

            # Prepare post data for WebSocket
            post_data = {
                'id': post.id,
                'caption': post.caption or '',
                'image_url': post.image.url if post.image else '',
                'content_type': post.content_type,
            }

            # Add content-specific data for the post link
            try:
                if post.content_type == 'blog':
                    blog = Blog.objects.get(id=post.content_id)
                    post_data['caption'] = blog.title
                    post_data['post_link'] = f"/blog/{blog.id}/"
                elif post.content_type == 'whitepaper':
                    whitepaper = Whitepaper.objects.get(id=post.content_id)
                    post_data['caption'] = whitepaper.title
                    post_data['post_link'] = f"/whitepaper/{whitepaper.id}/"
                elif post.content_type == 'insight':
                    insight = Insight.objects.get(id=post.content_id)
                    post_data['caption'] = insight.title
                    post_data['post_link'] = f"/insight/{insight.id}/"
                else:
                    post_data['post_link'] = f"/post/{post.id}/"
            except (Blog.DoesNotExist, Whitepaper.DoesNotExist, Insight.DoesNotExist) as e:
                logger.error(f"Associated content not found for post {post_id}: {str(e)}")
                return JsonResponse({"error": "Associated content not found"}, status=404)

            # Send the shared post and message to each recipient
            channel_layer = get_channel_layer()
            if not channel_layer:
                logger.error("Channel layer not configured")
                return JsonResponse({"error": "Channel layer not configured"}, status=500)

            for recipient_id in recipients:
                try:
                    recipient = CustomUser.objects.get(id=recipient_id)
                except CustomUser.DoesNotExist:
                    logger.error(f"Recipient {recipient_id} not found")
                    continue

                # Sanitize usernames to match ChatConsumer
                sender_clean = re.sub(r'[^a-zA-Z0-9]', '_', sender.username)
                receiver_clean = re.sub(r'[^a-zA-Z0-9]', '_', recipient.username)
                # Create the group name by sorting the sanitized usernames
                group_name = f"chat_{'_'.join(sorted([sender_clean, receiver_clean]))}"

                # Create the Message object for the shared post
                shared_post_message = Message.objects.create(
                    sender=sender,
                    receiver=recipient,
                    post=post,
                    timestamp=datetime.now(),
                    content=''
                )

                # If there's a message, create a follow-up Message object
                if message:
                    follow_up_message = Message.objects.create(
                        sender=sender,
                        receiver=recipient,
                        content=message,
                        timestamp=datetime.now(),
                    )

                # Send WebSocket message for the shared post
                async_to_sync(channel_layer.group_send)(
                    group_name,  # Use the sanitized, sorted group name
                    {
                        'type': 'new_message',
                        'message_id': shared_post_message.id,
                        'sender_name': sender.get_full_name() or sender.username,
                        'sender_profile_image': sender.userprofile.profile_image.url if (sender.userprofile and sender.userprofile.profile_image) else '/static/images/Profile-default.png',
                        'post': post_data,
                        'timestamp': shared_post_message.timestamp.strftime("%I:%M %p"),
                        'is_read': False,
                    }
                )

                # Send WebSocket message for the follow-up message, if it exists
                if message:
                    async_to_sync(channel_layer.group_send)(
                        group_name,  # Use the same group name
                        {
                            'type': 'new_message',
                            'message_id': follow_up_message.id,
                            'sender_name': sender.get_full_name() or sender.username,
                            'sender_profile_image': sender.userprofile.profile_image.url if (sender.userprofile and sender.userprofile.profile_image) else '/static/images/Profile-default.png',
                            'message': message,
                            'timestamp': follow_up_message.timestamp.strftime("%I:%M %p"),
                            'is_read': False,
                        }
                    )

            logger.info(f"Successfully shared post {post_id} with {len(recipients)} recipients")
            return JsonResponse({"success": True})

        except Post.DoesNotExist:
            logger.error(f"Post {post_id} not found")
            return JsonResponse({"error": "Post not found"}, status=404)
        except Exception as e:
            logger.error(f"Unexpected error in send_post_share: {str(e)}", exc_info=True)
            return JsonResponse({"error": "Internal server error"}, status=500)

    logger.warning("Invalid request method for send_post_share")
    return JsonResponse({"success": False}, status=400)


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from .models import Post

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


@login_required
def get_post_content(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    
    # Prepare the base post data
    post_data = {
        'author': post.user_profile.user.get_full_name() or post.user_profile.user.username,
        'profile_image': post.user_profile.profile_image.url if post.user_profile.profile_image else '/static/images/Profile-default.png',
        'caption': post.caption or '',  # Ensure caption is not null
        'image': post.image.url if post.image else '',
        'created_at': post.created_at.isoformat(),
        'content_type': post.content_type,  # Include content_type (asset_type)
    }

    # Add content-specific data based on content_type
    if post.content_type == 'blog':
        blog = get_object_or_404(Blog, id=post.content_id)
        post_data['content'] = {
            'title': blog.title,
            'thumbnail': blog.thumbnail.url if blog.thumbnail else '',
        }
    elif post.content_type == 'whitepaper':
        whitepaper = get_object_or_404(Whitepaper, id=post.content_id)
        post_data['content'] = {
            'title': whitepaper.title,
            'summary': whitepaper.summary,
        }
    elif post.content_type == 'insight':
        insight = get_object_or_404(Insight, id=post.content_id)
        post_data['content'] = {
            'title': insight.title,
            'summary': insight.summary,
        }

    return JsonResponse(post_data)



# profile Page View to Get post 
from django.http import JsonResponse
from .models import Post

def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    return render(request, 'post_detail.html', {'post': post})

#======================================ENd =================================== 

from .models import Post, Like
@login_required
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user_profile = request.user.userprofile
    like, created = Like.objects.get_or_create(user_profile=user_profile, post=post)

    if not created:
        like.delete()
    
    # Fetch updated like count
    like_count = post.likes.count()

    # Send real-time WebSocket update
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "timeline",  # WebSocket group
        {
            "type": "broadcast_like",
            "post_id": post.id,
            "like_count": like_count,
        }
    )

    return JsonResponse({'success': True, 'like_count': like_count})


from django.http import JsonResponse
from django.core.paginator import Paginator
from .models import Post

def load_more_posts(request):
    page = int(request.GET.get("page", 1))
    posts_per_page = 10
    posts = Post.objects.all().order_by('-created_at')
    paginator = Paginator(posts, posts_per_page)
    
    if page <= paginator.num_pages:
        page_obj = paginator.page(page)
        posts_data = [{
            'id': post.id,
            'caption': post.caption,
            'image': post.image.url if post.image else None,
            'user_profile_image': post.user_profile.profile_image.url if post.user_profile.profile_image else '/static/images/Profile-default.png',
            'username': post.user_profile.user.username,
            'full_name': post.user_profile.user.get_full_name(),
            'created_at': post.created_at.isoformat(),
            'like_count': post.likes.count(),
            'comment_count': post.comments.count(),
        } for post in page_obj]
        return JsonResponse({'posts': posts_data})
    return JsonResponse({'posts': []})


# views.py

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Post, Comment
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)

@login_required
def add_comment(request, post_id):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

    text = request.POST.get("comment", "").strip()
    parent_id = request.POST.get("parent_id")

    if not text:
        return JsonResponse({"success": False, "error": "Comment text is required"}, status=400)

    try:
        logger.info(f"Adding comment to post {post_id} by user {request.user.username}")
        post = get_object_or_404(Post, id=post_id)

        if not hasattr(request.user, 'userprofile'):
            logger.error(f"User {request.user.username} has no UserProfile")
            return JsonResponse({"success": False, "error": "User profile not found"}, status=500)

        parent_comment = None
        if parent_id and parent_id.isdigit():
            parent_comment = get_object_or_404(Comment, id=int(parent_id), post=post)

        comment = Comment.objects.create(
            user_profile=request.user.userprofile,
            post=post,
            text=text,
            parent=parent_comment
        )

        channel_layer = get_channel_layer()
        if channel_layer is None:
            logger.error("Channel layer not available")
            return JsonResponse({"success": False, "error": "WebSocket configuration error"}, status=500)

        profile_image_url = request.user.userprofile.profile_image.url if request.user.userprofile.profile_image else "/static/images/Profile-default.png"
        async_to_sync(channel_layer.group_send)(
            "timeline",
            {
                "type": "new_comment",
                "post_id": str(post.id),
                "comment_id": str(comment.id),
                "text": comment.text,
                "username": request.user.username,
                "full_name": request.user.get_full_name(),
                "created_at": comment.created_at.isoformat(),
                "parent_id": str(parent_id) if parent_comment else None,
                "comment_count": post.comments.count(),
                "user_profile_image": profile_image_url,  # Add this
            }
        )

        logger.info(f"Comment {comment.id} added successfully")
        return JsonResponse({
            "success": True,
            "comment_count": post.comments.count(),
            "comment_id": str(comment.id),
        })

    except Post.DoesNotExist:
        logger.error(f"Post {post_id} not found")
        return JsonResponse({"success": False, "error": "Post not found"}, status=404)
    except Comment.DoesNotExist:
        logger.error(f"Parent comment {parent_id} not found for post {post_id}")
        return JsonResponse({"success": False, "error": "Parent comment not found"}, status=404)
    except Exception as e:
        logger.exception(f"Error adding comment to post {post_id}: {str(e)}")
        return JsonResponse({"success": False, "error": f"Server error: {str(e)}"}, status=500)



# views.py
from django.http import JsonResponse
from .models import Comment, UserProfile
from django.contrib.auth.models import User

def get_replies(request, comment_id):
    try:
        parent_comment = Comment.objects.get(id=comment_id)
        replies = Comment.objects.filter(parent=parent_comment).select_related('user_profile__user')
        reply_data = [
            {
                "user_profile_image": reply.user_profile.profile_image.url if reply.user_profile.profile_image else '/static/images/Profile-default.png',
                "user_name": reply.user_profile.user.get_full_name(),
                "created_at": reply.created_at.isoformat(),  # Remove the "Z" suffix
                "text": reply.text
            }
            for reply in replies
        ]
        return JsonResponse({"replies": reply_data})
    except Comment.DoesNotExist:
        return JsonResponse({"replies": []}, status=404)

# Example Django views for comment actions
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Comment



def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        comment.text = request.POST.get('comment')
        comment.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

@login_required
def delete_comment(request, comment_id):
    """Delete a comment only if the user is the owner or an admin."""
    comment = get_object_or_404(Comment, id=comment_id)

    if request.user == comment.user_profile.user or request.user.is_staff:
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
    else:
        messages.error(request, "You are not authorized to delete this comment.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))  # Redirects back to the previous page



def follower_view(request):
    return render(request,'followers.html')

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import FollowRequest

@login_required
def follow_requests_view(request):
    """
    Display all pending follow requests for the logged-in user.
    """
    pending_requests = FollowRequest.objects.filter(to_user=request.user, status='pending')

    context = {
        'pending_requests': pending_requests
    }
    return render(request, 'requests.html', context)



# Search Logic 
from django.http import JsonResponse
from django.db.models import Q
from .models import UserProfile, Post
from DigitalAssets.models import Blog, Whitepaper, Insight
import logging
from difflib import SequenceMatcher


logger = logging.getLogger(__name__)


def ajax_search(request):
    try:
        query = request.GET.get('q', '').strip()
        if len(query) < 2:
            return JsonResponse({'people': [], 'posts': [], 'blogs': [], 'whitepapers': [], 'insights': []})

        # Get the current user (if authenticated) and their followed users
        current_user = request.user if request.user.is_authenticated else None
        followed_users = set()
        if current_user:
            followed_requests = FollowRequest.objects.filter(
                from_user=current_user,
                status='accepted'
            ).values_list('to_user_id', flat=True)
            followed_users = set(followed_requests)

        # Helper function to get a display name
        def get_display_name(user):
            if user:
                if user.full_name:
                    return user.full_name
                if user.first_name or user.last_name:
                    return f"{user.first_name} {user.last_name}".strip()
                return f"User {user.id}"
            return "Anonymous"

        # Helper function to calculate keyword relevance score
        def get_relevance_score(text, query):
            if not text:
                return 0
            return SequenceMatcher(None, text.lower(), query.lower()).ratio()

        # Search for people
        people = UserProfile.objects.filter(
            Q(user__full_name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(bio__icontains=query)
        ).select_related('user').annotate(
            follower_count=Count('user__received_requests', filter=Q(user__received_requests__status='accepted'))
        )
        people_data = [
            {
                'username': profile.user.username if profile.user else '',
                'full_name': get_display_name(profile.user),
                'bio': profile.bio,
                'profile_image': profile.profile_image.url if profile.profile_image else None,
                'follower_count': profile.follower_count,
                'is_followed': profile.user_id in followed_users if current_user else False,
                'relevance_score': max(
                    get_relevance_score(profile.user.full_name, query),
                    get_relevance_score(profile.user.username, query),
                    get_relevance_score(profile.bio, query)
                )
            }
            for profile in people
        ]
        people_data.sort(key=lambda x: (
            (1 if x['is_followed'] else 0) * 0.5 +
            x['relevance_score'] * 0.3 +
            x['follower_count'] * 0.0001
        ), reverse=True)
        people_data = people_data[:5]

        # Search for posts
        posts = Post.objects.filter(
            Q(caption__icontains=query) | Q(content_type='normal')
        ).select_related('user_profile__user').annotate(
            like_count=Count('likes')  # This is valid based on your Like model
        )
        posts_data = [
            {
                'id': post.id,
                'caption': post.caption,
                'full_name': get_display_name(post.user_profile.user if post.user_profile else None),
                'user_profile_image': post.user_profile.profile_image.url if post.user_profile and post.user_profile.profile_image else None,
                'like_count': post.like_count,
                'is_followed': post.user_profile.user_id in followed_users if post.user_profile and current_user else False,
                'relevance_score': get_relevance_score(post.caption, query)
            }
            for post in posts
        ]
        posts_data.sort(key=lambda x: (
            (1 if x['is_followed'] else 0) * 0.5 +
            x['relevance_score'] * 0.3 +
            x['like_count'] * 0.001
        ), reverse=True)
        posts_data = posts_data[:5]

        # Search for blogs (assuming Blog model exists but has no likes)
        blogs = Blog.objects.filter(
            Q(title__icontains=query) | Q(content__icontains=query),
            is_draft=False
        ).select_related('user_profile__user')  # No like_count annotation
        blogs_data = [
            {
                'id': blog.id,
                'title': blog.title,
                'content': blog.content,
                'full_name': get_display_name(blog.user_profile.user if blog.user_profile else None),
                'thumbnail': blog.thumbnail.url if blog.thumbnail else None,
                'is_followed': blog.user_profile.user_id in followed_users if blog.user_profile and current_user else False,
                'relevance_score': max(
                    get_relevance_score(blog.title, query),
                    get_relevance_score(blog.content, query)
                )
            }
            for blog in blogs
        ]
        blogs_data.sort(key=lambda x: (
            (1 if x['is_followed'] else 0) * 0.5 +
            x['relevance_score'] * 0.3
        ), reverse=True)
        blogs_data = blogs_data[:5]

        # Search for whitepapers (assuming Whitepaper model exists but has no likes)
        whitepapers = Whitepaper.objects.filter(
            Q(title__icontains=query) | Q(summary__icontains=query),
            is_draft=False
        ).select_related('user_profile__user')  # No like_count annotation
        whitepapers_data = [
            {
                'id': whitepaper.id,
                'title': whitepaper.title,
                'summary': whitepaper.summary,
                'full_name': get_display_name(whitepaper.user_profile.user if whitepaper.user_profile else None),
                'is_followed': whitepaper.user_profile.user_id in followed_users if whitepaper.user_profile and current_user else False,
                'relevance_score': max(
                    get_relevance_score(whitepaper.title, query),
                    get_relevance_score(whitepaper.summary, query)
                )
            }
            for whitepaper in whitepapers
        ]
        whitepapers_data.sort(key=lambda x: (
            (1 if x['is_followed'] else 0) * 0.5 +
            x['relevance_score'] * 0.3
        ), reverse=True)
        whitepapers_data = whitepapers_data[:5]

        # Search for insights (assuming Insight model exists but has no likes)
        insights = Insight.objects.filter(
            Q(title__icontains=query) | Q(summary__icontains=query),
            is_draft=False
        ).select_related('user_profile__user')  # No like_count annotation
        insights_data = [
            {
                'id': insight.id,
                'title': insight.title,
                'summary': insight.summary,
                'full_name': get_display_name(insight.user_profile.user if insight.user_profile else None),
                'is_followed': insight.user_profile.user_id in followed_users if insight.user_profile and current_user else False,
                'relevance_score': max(
                    get_relevance_score(insight.title, query),
                    get_relevance_score(insight.summary, query)
                )
            }
            for insight in insights
        ]
        insights_data.sort(key=lambda x: (
            (1 if x['is_followed'] else 0) * 0.5 +
            x['relevance_score'] * 0.3
        ), reverse=True)
        insights_data = insights_data[:5]

        return JsonResponse({
            'people': people_data,
            'posts': posts_data,
            'blogs': blogs_data,
            'whitepapers': whitepapers_data,
            'insights': insights_data
        })
    except Exception as e:
        logger.error(f"Error in ajax_search: {str(e)}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)




from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.db.models import Q
from .models import FollowRequest, CustomUser

@login_required
def send_follow_request(request, user_id):
    """
    Sends a follow request to another user.
    """
    to_user = get_object_or_404(CustomUser, id=user_id)

    if request.user == to_user:
        messages.error(request, "You cannot follow yourself!")
        return redirect('profile_detail', username=request.user.username)

    follow_request, created = FollowRequest.objects.get_or_create(
        from_user=request.user,
        to_user=to_user
    )

    if created:
        messages.success(request, f"Follow request sent to {to_user.username}.")
    else:
        messages.info(request, f"Follow request to {to_user.username} is already pending.")

    return redirect('profile_detail', username=to_user.username)


@login_required
def unfollow_user(request, user_id):
    """
    Unfollows a user (removes follow request).
    """
    to_user = get_object_or_404(CustomUser, id=user_id)

    deleted_count, _ = FollowRequest.objects.filter(
        (Q(from_user=request.user, to_user=to_user) | Q(from_user=to_user, to_user=request.user)),
        status='accepted'
    ).delete()

    if deleted_count > 0:
        messages.success(request, f"You have unfollowed {to_user.username}.")
    else:
        messages.warning(request, "No follow relationship found.")

    return redirect('profile_detail', username=to_user.username)


@login_required
def accept_follow_request(request, request_id):
    """
    Accepts a follow request.
    """
    follow_request = get_object_or_404(FollowRequest, id=request_id, to_user=request.user)

    follow_request.status = 'accepted'
    follow_request.save()

    messages.success(request, f"You are now following {follow_request.from_user.username}.")

    return redirect('requests')


@login_required
def decline_follow_request(request, request_id):
    """
    Declines a follow request.
    """
    follow_request = get_object_or_404(FollowRequest, id=request_id, to_user=request.user)
    follow_request.delete()

    messages.info(request, f"You declined {follow_request.from_user.username}'s follow request.")

    return redirect('requests')



from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser, FollowRequest

from django.db.models import Q

@login_required
def followers_list(request, username):
    user = get_object_or_404(CustomUser, username=username)
    
    # Users who have sent a follow request to this user
    sent_followers = CustomUser.objects.filter(sent_requests__to_user=user, sent_requests__status='accepted').distinct()
    
    # Users who have received a follow request from this user
    received_followers = CustomUser.objects.filter(received_requests__from_user=user, received_requests__status='accepted').distinct()

    # Combine both querysets
    followers = sent_followers.union(received_followers)

    # Get search query from GET request
    search_query = request.GET.get("q", "").strip()

    if search_query:
        followers = followers.filter(
            Q(username__icontains=search_query) | Q(first_name__icontains=search_query) | Q(last_name__icontains=search_query)
        )

    return render(request, "followers.html", {"followers": followers, "profile_user": user})



#  chat Messaging  ===============================================================================================================
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Message, CustomUser


from django.contrib import messages

@login_required
def chat_list(request):
    """Show only users who have messaged the logged-in user, sorted by the latest message."""
    messaged_users = CustomUser.objects.filter(
        Q(sent_messages__receiver=request.user) | Q(received_messages__sender=request.user)
    ).distinct()


    # Get groups where the logged-in user is a member
    groups = ChatGroup.objects.filter(members=request.user)

    # Fetch last message per user
    last_messages = {}
    user_last_messages = []
    new_message_count = 0  # Track new messages

    for user in messaged_users:
        last_message = Message.objects.filter(
            Q(sender=request.user, receiver=user) | Q(sender=user, receiver=request.user)
        ).order_by('-timestamp').first()

        last_messages[user.id] = last_message
        if last_message:
            user_last_messages.append((user, last_message.timestamp))
            
            # Check if the last message is unread
            if last_message.receiver == request.user and not last_message.is_read:
                new_message_count += 1

    # Sort users based on the latest message timestamp (newest first)
    sorted_users = sorted(user_last_messages, key=lambda x: x[1], reverse=True)
    sorted_users = [user[0] for user in sorted_users]  # Extract only user objects

    # Show toast notification if there are new messages
    

    return render(request, "chat_list.html", {
        "users": sorted_users,
        "last_messages": last_messages,
        "groups": groups
    })






from datetime import timedelta
from django.utils.timezone import localtime
from django.db.models import Q
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Message


from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message, Post
from DigitalAssets.models import Blog, Whitepaper, Insight
from django.http import JsonResponse
from django.db import models

from django.shortcuts import render, get_object_or_404
from django.utils.timezone import localtime
from datetime import timedelta
from django.db.models import Q
from .models import Message, CustomUser, UserProfile

def chat_room(request, username):
    """Show chat history between two users with date separators, supporting shared posts."""
    receiver = get_object_or_404(CustomUser, username=username)

    # Fetch messages between users, ordered by timestamp
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=receiver) | Q(sender=receiver, receiver=request.user)
    ).order_by("timestamp")

    # Mark received messages as read
    if messages.filter(receiver=request.user, is_read=False).exists():
        messages.filter(receiver=request.user, is_read=False).update(is_read=True)

    # Organize messages with date separators and post data
    today = localtime().date()
    yesterday = today - timedelta(days=1)
    chats = []
    last_date = None

    for message in messages:
        message_date = localtime(message.timestamp).date()

        # Add date separator only if the date changes
        if message_date != last_date:
            if message_date == today:
                chats.append({"date": "Today"})
            elif message_date == yesterday:
                chats.append({"date": "Yesterday"})
            else:
                chats.append({"date": message_date.strftime("%B %d, %Y")})
            last_date = message_date

        # Get sender's profile image from UserProfile
        sender_profile = UserProfile.objects.filter(user=message.sender).first()
        sender_profile_image = (
            sender_profile.profile_image.url 
            if sender_profile and sender_profile.profile_image 
            else '/static/images/Profile-default.png'
        )

        # Check if the message was sent by the logged-in user
        is_sent_by_user = message.sender == request.user

        # Add message with post preview if it's a shared post
        if message.is_post_share():
            post = message.post
            post_data = {
                'id': post.id,
                'image_url': post.image.url if post.image else None,
                'content_type': post.content_type,
            }
            # Set caption and post_link based on content_type
            if post.content_type == 'blog':
                blog = Blog.objects.get(id=post.content_id)
                post_data['caption'] = blog.title
                post_data['post_link'] = f"/blog/{blog.id}/"
            elif post.content_type == 'whitepaper':
                whitepaper = Whitepaper.objects.get(id=post.content_id)
                post_data['caption'] = whitepaper.title
                post_data['post_link'] = f"/whitepaper/{whitepaper.id}/"
            elif post.content_type == 'insight':
                insight = Insight.objects.get(id=post.content_id)
                post_data['caption'] = insight.title
                post_data['post_link'] = f"/insight/{insight.id}/"
            else:
                post_data['caption'] = post.caption or ''
                post_data['post_link'] = f"/post/{post.id}/"

            chats.append({
                'post': post_data,
                'sender_name': message.sender.get_full_name() or message.sender.username,
                'sender_profile_image': sender_profile_image,
                'timestamp': message.timestamp.strftime("%I:%M %p"),
                'is_sent_by_user': is_sent_by_user,
            })
        else:
            chats.append({
                'message': message.content,
                'message_id': message.id,
                'sender_name': message.sender.get_full_name() or message.sender.username,
                'sender_profile_image': sender_profile_image,
                'timestamp': message.timestamp.strftime("%I:%M %p"),
                'is_read': message.is_read,
                'is_sent_by_user': is_sent_by_user,
            })

    return render(request, 'chat_room.html', {
        'receiver': receiver,
        'chats': chats,
    })

@login_required
def send_message(request):
    """AJAX call to send a message."""
    if request.method == "POST":
        receiver_id = request.POST.get("receiver_id")
        content = request.POST.get("content")
        receiver = get_object_or_404(CustomUser, id=receiver_id)
        
        message = Message.objects.create(sender=request.user, receiver=receiver, content=content)
        
        return JsonResponse({"message": message.content, "timestamp": message.timestamp.strftime("%Y-%m-%d %H:%M")})

    return JsonResponse({"error": "Invalid request"}, status=400)


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import ChatGroup
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

@login_required
def create_group(request):
    if request.method == "POST":
        group_name = request.POST.get("group_name")
        group_slug = slugify(group_name)
        group_picture = request.FILES.get("group_picture")
        members = request.POST.getlist("members")

        # Create new chat group
        group = ChatGroup.objects.create(
            name=group_name, 
            creator=request.user, 
            group_picture=group_picture
        )
        group.members.add(*members)  # Add selected members
        group.members.add(request.user)  # Add creator to the group

        return redirect("chat_list")  # Redirect to group listing page

    users = User.objects.exclude(id=request.user.id)
    return render(request, "chat_list.html", {"users": users})




from django.shortcuts import render, Http404
from django.contrib.auth.decorators import login_required
from django.utils.text import slugify
from .models import ChatGroup, GroupMessage

@login_required
def chat_group_room(request, group_name):
    # Sanitize the incoming group name using slugify
    sanitized_group_name = slugify(group_name)  # e.g. "New Group" -> "new-group"
    
    group = None
    # Iterate through all groups and compare their slugified names
    for g in ChatGroup.objects.all():
        if slugify(g.name) == sanitized_group_name:
            group = g
            break

    if group is None:
        raise Http404("No ChatGroup matches the given query.")

    # Retrieve all messages for the group, ordered by timestamp
    chats = GroupMessage.objects.filter(group=group).order_by("timestamp")
    
    context = {
        "group": group,
        "group_name": sanitized_group_name,
        "chats": chats,
    }
    return render(request, "group_chat.html", context)

@login_required
def remove_group_member(request, group_id, member_id):
    """
    Allow only the group admin (creator) to remove a member.
    """
    group = get_object_or_404(ChatGroup, id=group_id)
    member = get_object_or_404(CustomUser, id=member_id)
    
    if request.user != group.creator:
        messages.error(request, "Only the group admin can remove members.")
        return redirect("chat_group_room", group_name=group.name)
    
    if member == group.creator:
        messages.error(request, "You cannot remove the group admin.")
        return redirect("chat_group_room", group_name=group.name)
    
    group.members.remove(member)
    messages.success(request, f"{member.get_full_name()} has been removed from the group.")
    return redirect("chat_group_room", group_name=group.name)

@login_required
def leave_group(request, group_id):
    """
    Allow any member (except the admin) to leave the group.
    """
    group = get_object_or_404(ChatGroup, id=group_id)
    
    if request.user == group.creator:
        messages.error(request, "Admin cannot leave the group. Consider deleting the group instead.")
        return redirect("chat_group_room", group_name=group.name)
    
    group.members.remove(request.user)
    messages.success(request, "You have left the group.")
    return redirect("chat_list")  # Adjust redirect as 


from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from Users.models import CustomUser  # Adjust as necessary
from .models import ChatGroup

@login_required
def add_group_members(request, group_id):
    """
    AJAX view to allow group admin to add new members.
    Expects a POST with a comma‐separated string of user IDs in the "members" field.
    """
    if request.method == "POST":
        group = get_object_or_404(ChatGroup, id=group_id)
        # Only the group creator (admin) can add members.
        if request.user != group.creator:
            return JsonResponse({"status": "error", "message": "Only group admin can add members."}, status=403)
        
        member_ids_str = request.POST.get("members", "")
        if not member_ids_str:
            return JsonResponse({"status": "error", "message": "No members provided."}, status=400)
        
        try:
            member_ids = [int(x.strip()) for x in member_ids_str.split(",") if x.strip().isdigit()]
        except ValueError:
            return JsonResponse({"status": "error", "message": "Invalid member IDs."}, status=400)
        
        new_members = []
        for member_id in member_ids:
            try:
                user = CustomUser.objects.get(id=member_id)
                if user not in group.members.all():
                    group.members.add(user)
                    new_members.append(user.get_full_name())
            except CustomUser.DoesNotExist:
                continue
        
        if new_members:
            return JsonResponse({"status": "success", "message": f"Added: {', '.join(new_members)}"})
        else:
            return JsonResponse({"status": "error", "message": "No new members added."}, status=400)
    return JsonResponse({"status": "error", "message": "Invalid request method."}, status=400)



from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from Users.models import CustomUser  # Adjust the import as needed

@login_required
def search_users(request):
    query = request.GET.get("q", "")
    if query:
        # Filter users by username, first name, or last name.
        users = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).distinct()[:10]
        
        results = []
        for user in users:
            results.append({
                "id": user.id,
                "username": user.username,
                "full_name": user.get_full_name() or user.username,
            })
        return JsonResponse({"users": results})
    return JsonResponse({"users": []})



from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from Users.models import CustomUser  # Adjust the import path as needed

@login_required
def ajax_search_users(request):
    query = request.GET.get("q", "")
    if query:
        # Filter users by username, first name, or last name (case-insensitive)
        users = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).distinct()[:10]
        
        results = []
        for user in users:
            results.append({
                "id": user.id,
                "username": user.username,
                "full_name": user.get_full_name() or user.username,
            })
        return JsonResponse({"users": results})
    return JsonResponse({"users": []})



from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from .models import ChatGroup
from django.contrib import messages

@login_required
def update_group_details(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    # Optionally, restrict editing to group members or the group creator only.
    if request.method == "POST":
        group.name = request.POST.get("name", group.name)
        if request.FILES.get("group_picture"):
            group.group_picture = request.FILES["group_picture"]
        group.save()
        messages.success(request, "Group details updated successfully.")
        return redirect("chat_group_room", group_name=group.name)
    return render(request, "edit_group_details.html", {"group": group})

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ChatGroup

@login_required
def delete_group(request, group_id):
    group = get_object_or_404(ChatGroup, id=group_id)
    # Only the creator can delete the group.
    if request.user != group.creator:
        messages.error(request, "Only the group creator can delete this group.")
        return redirect("chat_group_room", group_name=group.name)
    
    if request.method == "POST":
        group.delete()
        messages.success(request, "Group deleted successfully.")
        return redirect("chat_list")  # Or wherever you want to redirect after deletion.
    
    # Render a confirmation page (optional)
    return render(request, "confirm_delete_group.html", {"group": group})


#  saved post ===================================================================================================================

from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Post, UserProfile

@login_required
def saved_posts(request):
    user_profile = request.user.userprofile
    saved_posts = user_profile.saved_posts.all()
    return render(request, 'saved_posts.html', {'saved_posts': saved_posts})

@login_required
def save_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user_profile = request.user.userprofile
    
    if post in user_profile.saved_posts.all():
        user_profile.saved_posts.remove(post)
        saved = False
    else:
        user_profile.saved_posts.add(post)
        saved = True
    
    return JsonResponse({'saved': saved})

@login_required
def unsave_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user_profile = request.user.userprofile
    
    if post in user_profile.saved_posts.all():
        user_profile.saved_posts.remove(post)
    
    return JsonResponse({'unsaved': True})




from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from .models import Organization
import json


def organization_form(request):
    context = {
        'industry_choices': Organization.INDUSTRY_CHOICES,
        'business_type_choices': Organization.BUSINESS_TYPE_CHOICES,
        'nature_choices': Organization.NATURE_CHOICES,
        'education_choices': Organization.EDUCATION_CHOICES,
    }
    return render(request, 'org_form.html', context)


@csrf_protect
def submit_organization(request):
    if request.user.user_type != 'organizational':
        return JsonResponse({
            'status': 'error',
            'message': 'Only organizational users can submit this form'
        }, status=403)

    if request.method == 'POST':
        try:
            data = request.POST

            # Check if organization already exists for this user
            if Organization.objects.filter(user=request.user).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Organization profile already exists'
                }, status=400)

            # Create new Organization instance with user relationship
            organization = Organization(
                user=request.user,  # Link to the current user
                industry_type=data.get('industry_type'),
                organization_name=data.get('organization_name'),
                total_employees=int(data.get('total_employees', 0)),
                description=data.get('description'),
                revenue=float(data.get('revenue', 0)),
                gst_number=data.get('gst_number'),
                start_year=int(data.get('start_year', 2000)),
                business_type=data.get('business_type'),
                business_nature=data.get('business_nature'),
                challenges=data.get('challenges'),
                digital_assets=data.get('digital_assets'),
                desired_assets=data.get('desired_assets'),
                skills=data.get('skills'),
                wish_to_expand=data.get('wish_to_expand') == 'true',
                locations=data.get('locations'),
                education=data.get('education'),
                website_link=data.get('website_link'),
                open_positions=data.get('open_positions'),
                willing_to_collaborate=data.get('willing_to_collaborate') == 'true'
            )
            organization.save()

            return JsonResponse({
                'status': 'success', 
                'message': 'Organization data saved successfully',
                'redirect_url': reverse('dashboard_new')  # Add redirect URL
            })

        except ValueError as e:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid data format: {str(e)}'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': f'An error occurred: {str(e)}'
            }, status=500)

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    }, status=405)



# views.py
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Degree, Specialization, Industry, User_form
from django.conf import settings
import json

@login_required
def user_form(request):
    degrees = Degree.objects.all()
    industries = Industry.objects.all()

    if request.method == 'POST':
        try:
            # Parse JSON fields
            top_skills = json.loads(request.POST.get('top_skills', '[]'))
            career_goal_skills = json.loads(request.POST.get('career_goal_skills', '[]'))
            certifications = json.loads(request.POST.get('certifications', '[]'))

            # Create User_form instance
            user_profile = User_form(
                user=request.user,
                highest_degree_id=request.POST.get('highest_degree'),
                specialization_id=request.POST.get('specialization'),
                graduation_year=request.POST.get('graduation_year'),
                
                current_occupation=request.POST.get('current_occupation'),
                current_organization=request.POST.get('current_organization'),
                years_of_experience=request.POST.get('experience_years', 0),
                top_skills=top_skills,
                is_fresher=request.POST.get('is_fresher') == 'on',
                on_career_break=request.POST.get('on_career_break') == 'on',
                preferred_industry_id=request.POST.get('preferred_industry'),
                desired_job_role=request.POST.get('desired_job_role'),
                specific_position=request.POST.get('specific_position'),
                career_goal_skills=career_goal_skills,
                certifications=certifications,
                looking_for_career_switch=request.POST.get('looking_for_career_switch') == 'true',
                willing_to_take_projects=request.POST.get('willing_to_take_projects') == 'true',
                interested_in_new_course=request.POST.get('interested_in_new_course') == 'true',
                portfolio_link=request.POST.get('portfolio_link'),
                ideal_organization=request.POST.get('ideal_organization')
            )
            user_profile.save()
            return redirect('dashboard_new')
        except Exception as e:
            print(e)
            return render(request, 'user_form.html', {
                'degrees': degrees,
                'industries': industries,
                'error': str(e)
            })

    return render(request, 'user_form.html', {
        'degrees': degrees,
        'industries': industries
    })

def get_specializations(request):
    degree_id = request.GET.get('degree')
    if degree_id:
        specializations = Specialization.objects.filter(degree_id=degree_id).values('id', 'name')
        return JsonResponse(list(specializations), safe=False)
    return JsonResponse([], safe=False)