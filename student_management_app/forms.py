from django import forms
from .models import Teacher

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['subject_taught', 'department', 'contact_number','cnic'] # Include fields you want admin to editfrom django import forms
from django import forms
from .models import StudentProfile

class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = StudentProfile
        fields = ['semester', 'contact_number', 'cnic']
        