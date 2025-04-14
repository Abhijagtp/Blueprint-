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



from django import forms
from .models import Organization

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = [
            'organization_name',  # Updated from 'name'
            'description',
            'website_link',      # Updated from 'website'
            'start_year',        # Updated from 'founded_date'
            'locations',         # Updated from 'location'
            'industry_type',
            'business_type',
            'business_nature',
        ]
        widgets = {
            'organization_name': forms.TextInput(attrs={'required': True}),
            'description': forms.Textarea(attrs={'rows': 4}),
            'website_link': forms.URLInput(),
            'start_year': forms.NumberInput(attrs={'type': 'number'}),
            'locations': forms.TextInput(attrs={'placeholder': 'e.g., New York, London'}),
            'industry_type': forms.Select(),
            'business_type': forms.Select(),
            'business_nature': forms.Select(),
        }