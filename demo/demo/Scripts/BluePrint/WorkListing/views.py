from django.shortcuts import render

# Create your views here.
def work_listing(request):
    return render(request, 'work_listing.html')

from django.shortcuts import render
from .models import Project

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Project

@login_required
def explore_projects(request):
    # Fetch all active projects with applications open
    projects = Project.objects.filter(is_active=True, applications_open=True)

    # Preprocess skills for each project
    for project in projects:
        if project.skills_required:
            project.skills_list = [skill.strip() for skill in project.skills_required.split(',')]
        else:
            project.skills_list = []

    return render(request, 'explore_projects.html', {'projects': projects})

def application_status(request):
    user = request.user
    applications = ProjectRequest.objects.filter(professional=user).select_related('project')

    return render(request, 'application_status.html', {'applications': applications})



from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ProjectRequest, ProjectSubmission

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import ProjectRequest, ProjectSubmission

@login_required
def project_status(request):
    # Fetch accepted projects that are in progress (no submission yet)
    in_progress_projects = ProjectRequest.objects.filter(
        professional=request.user, 
        status='accepted'
    ).exclude(
        submissions__isnull=False  # Exclude projects with submissions
    ).select_related('project')

    # Fetch completed submissions (projects with submissions)
    completed_submissions = ProjectSubmission.objects.filter(
        project_request__professional=request.user
    ).select_related('project_request__project')

    context = {
        'in_progress_projects': in_progress_projects,
        'completed_submissions': completed_submissions,
    }
    
    return render(request, 'project_status.html', context)


def invoice(request):
    return render(request, 'invoice.html')

def search_talent(request):
    return render(request, 'Search_talent.html')


from django.shortcuts import render
from .models import Project

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Project
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Project, ProjectRequest, ProjectSubmission

@login_required
def post_project(request):
    # Fetch posted projects (active and applications open)
    posted_projects = Project.objects.filter(
        org=request.user, is_active=True, applications_open=True
    ).order_by('-created_at')

    # Preprocess skills for posted projects
    for project in posted_projects:
        if project.skills_required:
            project.skills_list = [skill.strip() for skill in project.skills_required.split(',')]
        else:
            project.skills_list = []

    # Fetch running projects (active but applications closed)
    running_projects = Project.objects.filter(
        org=request.user, is_active=True, applications_open=False
    ).order_by('-created_at')

    # Fetch assigned professionals for running projects and preprocess skills
    running_projects_with_assignees = []
    for project in running_projects:
        # Preprocess skills for running projects
        if project.skills_required:
            project.skills_list = [skill.strip() for skill in project.skills_required.split(',')]
        else:
            project.skills_list = []

        # Fetch the assigned professional (if any)
        assigned_professional = ProjectRequest.objects.filter(
            project=project, status="accepted"
        ).select_related("professional__userprofile").first()

        running_projects_with_assignees.append({
            "project": project,
            "assigned_professional": assigned_professional.professional if assigned_professional else None,
            "has_accepted_professional": assigned_professional is not None
        })

    # Fetch completed projects
    completed_projects = Project.objects.filter(
        requests__submissions__status__in=["accepted", "rejected"]
    ).distinct()

    # Preprocess skills for completed projects
    for project in completed_projects:
        if project.skills_required:
            project.skills_list = [skill.strip() for skill in project.skills_required.split(',')]
        else:
            project.skills_list = []

    return render(request, 'post_project.html', {
        'posted_projects': posted_projects,
        'running_projects_with_assignees': running_projects_with_assignees,
        'completed_projects': completed_projects,
    })


from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Project
from django.contrib.auth.decorators import login_required
import json

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
from .models import Project

@login_required
@require_POST
def create_project(request):
    data = json.loads(request.body)
    domain = data.get("domain")
    description = data.get("description")
    experience_required = data.get("experience_required")
    skills_required = data.get("skills_required", [])  # List of skills
    submission_date = data.get("submission_date")
    payment = data.get("payment")

    # Clean and deduplicate skills
    skills_required = [skill.strip() for skill in skills_required if skill.strip()]
    skills_required = list(dict.fromkeys(skills_required))  # Remove duplicates
    skills_str = ",".join(skills_required) if skills_required else ""

    # Debug: Log the skills being saved
    print("Skills being saved:", skills_str)

    project = Project.objects.create(
        org=request.user,
        domain=domain,
        description=description,
        experience_required=experience_required,
        skills_required=skills_str,
        submission_date=submission_date,
        payment=payment,
    )
    return JsonResponse({"message": "Project created successfully", "project_id": project.id})

from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Project 
from Users.models import Skill
from datetime import datetime, timezone

def get_project(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    
    # Get logged-in user's skills
    user_skills = list(Skill.objects.filter(user_profile=request.user.userprofile).values_list('skill_name', flat=True))

    # Compare with project skills
    matched_skills = [skill for skill in project.skills_required if skill in user_skills]
    total_skills = len(project.skills_required)
    matched_count = len(matched_skills)

    # Calculate posted days ago
    posted_days_ago = (datetime.now(timezone.utc) - project.created_at).days

    data = {
        "org": project.org.get_full_name(),
        "domain": project.domain,
        "description": project.description.replace("\n", "<br>"),  # Preserve line breaks
        "experience_required": project.experience_required,
        "skills_required": project.skills_required,
        
        "submission_date": project.submission_date.strftime("%d %b, %Y"),
        "payment": str(project.payment),
        "matched_skills": matched_skills,
        "matched_count": matched_count,
        "total_skills": total_skills,
        "posted_days_ago": posted_days_ago,
        "posted_date": project.created_at.strftime("%d %b, %Y"),
    }
    
    return JsonResponse(data)


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from.models import Project, ProjectRequest

@csrf_exempt
def apply_project(request, project_id):
    if not request.user.is_authenticated:
        return JsonResponse({"success": False, "error": "User not logged in"}, status=401)

    project = Project.objects.filter(id=project_id, is_active=True).first()
    if not project:
        return JsonResponse({"success": False, "error": "Project not found"}, status=404)

    # Check if the user has already applied
    existing_request = ProjectRequest.objects.filter(project=project, professional=request.user).exists()
    if existing_request:
        return JsonResponse({"success": False, "error": "Already applied"}, status=400)

    # Create the project request
    ProjectRequest.objects.create(project=project, professional=request.user, status='pending')

    return JsonResponse({"success": True})


#  check status 
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from .models import Project, ProjectRequest
from Users.models import Skill,UserProfile

def project_applicants(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    applicants = ProjectRequest.objects.filter(project=project).select_related('professional__userprofile')

    applicants_data = [
        {
            "application_id": applicant.id,  # ✅ Use `ProjectRequest.id`, NOT `professional.id`
            "name": applicant.professional.get_full_name(),
            "bio": applicant.professional.userprofile.bio if hasattr(applicant.professional, 'userprofile') else "No bio available",
            "profile_image": applicant.professional.userprofile.profile_image.url if applicant.professional.userprofile and applicant.professional.userprofile.profile_image else "/static/default-profile.png",
            "status": applicant.status  # Include status to handle button visibility
        }
        for applicant in applicants
    ]

    return JsonResponse({"applicants": applicants_data})




from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ProjectRequest  # Replace 'your_app' with actual app name

@csrf_exempt
def update_application_status(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON correctly
            application_id = int(data.get("application_id"))  # Ensure ID is an integer
            status = data.get("status")

            print(f"Received ID: {application_id}, Status: {status}")  # Debugging log

            # Fetch the ProjectRequest object
            try:
                application = ProjectRequest.objects.get(id=application_id)
                print(f"Found application: {application}")  # Debugging log
            except ProjectRequest.DoesNotExist:
                print(f"Application ID {application_id} not found!")  # Debugging log
                return JsonResponse({"error": "Application not found."}, status=404)

            # Update the status
            application.status = status
            application.save()

            return JsonResponse({"message": "Status updated successfully.", "success": True})
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            print(f"Unexpected error: {e}")  # Debugging log
            return JsonResponse({"error": "An unexpected error occurred."}, status=500)
    
    return JsonResponse({"error": "Invalid request."}, status=400)




from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Project

@csrf_exempt
def toggle_project_applications(request, project_id):
    """Enable or disable applications for a project."""
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            action = data.get("action")  # "stop" or "continue"

            project = get_object_or_404(Project, id=project_id)

            if action == "stop":
                project.applications_open = False
            elif action == "continue":
                project.applications_open = True
            else:
                return JsonResponse({"error": "Invalid action."}, status=400)

            project.save()
            return JsonResponse({
                "success": True,
                "applications_open": project.applications_open,
                "message": f"Applications have been {'stopped' if action == 'stop' else 'reopened'}."
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data."}, status=400)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)




from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json
from .models import ProjectRequest, ProjectSubmission, Project

@csrf_exempt  # Remove if using CSRF tokens
@login_required
def submit_project(request, project_id):
    if request.method == "POST":
        try:
            # Ensure the user is a professional
            if request.user.user_type != 'professional':
                return JsonResponse({"success": False, "error": "Only professionals can submit projects"}, status=403)

            # Parse JSON data
            data = json.loads(request.body)
            submission_url = data.get("submission_url")
            submission_file = request.FILES.get("submission_file")  # Optional: Handle file uploads
            comments = data.get("comments", "")

            if not submission_url and not submission_file:
                return JsonResponse({"success": False, "error": "No URL or file provided"}, status=400)

            # Debugging: Check if the project and request exist
            try:
                project_request = ProjectRequest.objects.get(
                    project_id=project_id, 
                    professional=request.user, 
                    status='accepted'
                )
            except ProjectRequest.DoesNotExist:
                # Detailed error message
                error_msg = "No approved project request found. "
                if not ProjectRequest.objects.filter(project_id=project_id).exists():
                    error_msg += f"Project ID {project_id} has no requests."
                elif not ProjectRequest.objects.filter(professional=request.user).exists():
                    error_msg += "You have not applied to any projects."
                elif not ProjectRequest.objects.filter(project_id=project_id, professional=request.user).exists():
                    error_msg += f"You have not applied to project ID {project_id}."
                else:
                    error_msg += f"Your request for project ID {project_id} is not approved."
                return JsonResponse({"success": False, "error": error_msg}, status=404)

            # Check for existing submission
            if ProjectSubmission.objects.filter(project_request=project_request).exists():
                return JsonResponse({"success": False, "error": "Submission already exists for this project"}, status=400)

            # Create submission
            submission = ProjectSubmission(
                project_request=project_request,
                submission_url=submission_url,
                submission_file=submission_file,
                comments=comments
            )
            submission.save()

            return JsonResponse({"success": True, "message": "Submission created successfully"})
        
        except json.JSONDecodeError:
            return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method"}, status=405)

from django.shortcuts import render
from .models import ProjectSubmission

@login_required
def project_approval(request):
    # Fetch submissions that are pending evaluation
    pending_submissions = ProjectSubmission.objects.filter(status=ProjectSubmission.PENDING)
    return render(request, 'project_approval.html', {'pending_submissions': pending_submissions})




from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import ProjectSubmission

def evaluate_project(request, submission_id):
    submission = get_object_or_404(ProjectSubmission, id=submission_id)

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "accept":
            # Update status to accepted
            submission.status = ProjectSubmission.ACCEPTED
            # Save rating and feedback if provided
            submission.rating = request.POST.get("rating")
            submission.feedback = request.POST.get("feedback")
            messages.success(request, "Submission has been accepted and feedback saved.")
        elif action == "reject":
            # Update status to rejected
            submission.status = ProjectSubmission.REJECTED
            messages.warning(request, "Submission has been rejected.")

        # Save the updated submission
        submission.updated_by = request.user
        submission.save()

    return redirect("project_approval")  # Redirect to the evaluation page
