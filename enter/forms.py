from django import forms


class DateInput(forms.DateInput):
    input_type = 'date'

class StudentEntryExitForm(forms.Form):
    student_id = forms.CharField(max_length=255)

class DateForm(forms.Form):
    date = forms.DateField(widget=DateInput)

    