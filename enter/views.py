import datetime
from django.shortcuts import render
from .models import record
from .forms import recordform, StudentEntryExitForm
from django.views.generic import View
from datetime import datetime
import time
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages




def library(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        try:
            student = record.objects.get(rollno=student_id,status='IN')
            if student.exittime is None:
                student.exittime = datetime.now()
                student.status = 'OUT'
                student.save()
                message="Student with rollno: "+student_id+" has exited the library at "+str(datetime.now().replace(microsecond=0))
            else:
                    record.objects.create(rollno=student_id, entrytime=datetime.now())
                    message="Student with rollno: "+student_id+" has entered the library at "+str(datetime.now().replace(microsecond=0))
        except record.DoesNotExist:
            record.objects.create(rollno=student_id, entrytime=datetime.now())
            message="Student with rollno: "+student_id+" has entered the library at "+str(datetime.now().replace(microsecond=0))
    return render(request, 'library.html', {'form': StudentEntryExitForm(),'message':message})



def date_entries(request, date):
  
    start_date = datetime.strptime(date + " 00:00:00", '%Y-%m-%d %H:%M:%S').date()
    end_date = datetime.strptime(date + " 23:59:59", '%Y-%m-%d %H:%M:%S').date()
    date_entries = record.objects.filter(entrytime__range=(start_date,end_date))
    context = {'date_entries': date_entries}
    return render(request, 'date_entries.html', context)
