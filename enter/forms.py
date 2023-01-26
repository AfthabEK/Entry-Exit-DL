from django import forms
from .models import record

class recordform(forms.ModelForm):
    class Meta:
        model = record
        fields = ('rollno',)

class StudentEntryExitForm(forms.Form):
    student_id = forms.CharField(max_length=255)