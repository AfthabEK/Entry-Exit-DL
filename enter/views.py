import datetime,csv
from django.shortcuts import render
from .models import record
from .forms import StudentEntryExitForm, DateForm
from datetime import datetime
from django.shortcuts import redirect
from datetime import date
from django.http import HttpResponse




def library(request):
    message=""
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        today = date.today()
        
        try:
            student = record.objects.get(rollno=student_id,status='IN')
            if student.exittime is None:
                student.exittime = current_time
                student.status = 'OUT'
                student.save()
                message="Student with rollno: "+student_id+" has exited the library at "+str(current_time)
            else:
                    record.objects.create(rollno=student_id, entrytime=datetime.now(),date=today)
                    message="Student with rollno: "+student_id+" has entered the library at "+str(current_time)
        except record.DoesNotExist:
            record.objects.create(rollno=student_id, entrytime=datetime.now(),date=today)
            message="Student with rollno: "+student_id+" has entered the library at "+str(current_time)
    return render(request, 'library.html', {'form': StudentEntryExitForm(),'message':message})





#show all records
def allrecords(request):
    students = record.objects.all()
    form = DateForm(request.POST)
    return render(request, 'allrecords.html', {'students': students, 'form': form})

# view to display records of a particular date
def records(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        students = record.objects.filter(date=date)
        return render(request, 'records.html', {'students': students, 'form': DateForm(),'date': date})
    return render(request, 'records_form.html', {'form': DateForm()})

# view to display records by status
def recordsbystatus(request):
        students = record.objects.filter(status='IN')
        return render(request, 'current.html', {'students': students})

# view to export records to csv
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Roll No', 'Entry Time', 'Exit Time', 'Date'])
    for row in record.objects.all().values_list('rollno', 'entrytime', 'exittime', 'date'):
        writer.writerow(row)
    response['Content-Disposition'] = 'attachment; filename="records.csv"'
    return response

# view to export records of a particular date to csv
def exportbydate(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['Roll No', 'Entry Time', 'Exit Time', 'Date'])
        for row in record.objects.filter(date=date).values_list('rollno', 'entrytime', 'exittime'):
            writer.writerow(row)
        response['Content-Disposition'] = 'attachment; filename="records.csv"'
        return response
    else:
        return render(request, 'records_formcsv.html', {'form': DateForm()})