# forms.py
from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    skills_required = forms.CharField(
        widget=forms.TextInput(attrs={'placeholder': 'Enter skills separated by commas'}),
        help_text="Enter skills separated by commas (e.g., Python, Django, JavaScript)"
    )

    class Meta:
        model = Project
        fields = [
            'domain', 'description', 'experience_required',
            'skills_required', 'submission_date', 'payment'
        ]
        widgets = {
            
            'submission_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_skills_required(self):
        skills = self.cleaned_data['skills_required']
        return [skill.strip() for skill in skills.split(',')]