import datetime
from django.shortcuts import render
from .models import Student
from .forms import LibraryForm
from django.views.generic import View
from datetime import datetime


def library(request):
    if request.method == 'POST':
        form = LibraryForm(request.POST)
        if form.is_valid():
            roll_number = form.cleaned_data['roll_number']
            try:
                student = Student.objects.get(roll_number=roll_number)
                if student.entry_time and not student.exit_time:
                    student.exit_time = datetime.now()
                    student.save()
                    message = "Exit time recorded for student with roll number {}".format(roll_number)
                else:
                    message = "Invalid request"
            except Student.DoesNotExist:
                student = Student(roll_number=roll_number)
                student.entry_time = datetime.now()
                student.save()
                message = "Entry time recorded for student with roll number {}".format(roll_number)
        else:
            message = "Invalid form data"
    else:
        form = LibraryForm()
        message = ""
    return render(request, 'library.html', {'form': form, 'message': message})
