from django import forms

class LibraryForm(forms.Form):
    roll_number = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'class': 'form-control'}))