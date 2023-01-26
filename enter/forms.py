from django import forms
from .models import record

class entryform(forms.ModelForm):
    class Meta:
        model = record
        fields = ['rollno']