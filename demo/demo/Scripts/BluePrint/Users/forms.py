from django import forms
from .models import UserProfile, Experience, Education, Skill

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['bio', 'website']

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['title', 'organization_name', 'is_current', 'from_date', 'to_date', 'skills_gained']

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institute_name', 'degree', 'field_of_study', 'is_studying', 'start_date', 'end_date']

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['skill_name']


from django import forms
from .models import Certification

class CertificationForm(forms.ModelForm):
    skills_gained = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter skills separated by commas'}),
        required=False
    )

    class Meta:
        model = Certification
        fields = ['course_name', 'issuing_organization', 'completion_date', 'certificate_file', 'skills_gained']

from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'technologies', 'image1', 'image2']
        widgets = {
            'technologies': forms.TextInput(attrs={'placeholder': 'Enter technologies, separated by commas'})
        }

