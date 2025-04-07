


from django import forms

from .models import Course, Lesson


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = '__all__'
        widgets = {
            'subcategory': forms.Select(),  # Force <select> element
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Load initial subcategory choices if category exists
        if self.instance.category:
            self.fields['subcategory'].choices = self.get_subcategory_choices()

  

class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ['title', 'video']