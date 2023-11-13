from django import forms


class DateInput(forms.DateInput):
    input_type = 'date'

class DateForm(forms.Form):
    date = forms.DateField(widget=DateInput)

class MonthForm(forms.Form):
    month = forms.DateField(widget=DateInput)

    
