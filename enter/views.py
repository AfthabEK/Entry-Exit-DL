import datetime,csv
from django.shortcuts import render
from .models import record
from .forms import StudentEntryExitForm, DateForm, MonthForm
from datetime import datetime
from django.shortcuts import redirect
from datetime import date
from django.http import HttpResponse
import socket

readerIP='192.168.230.16'
readerPort=100

def library(request):
    count=record.objects.filter(status='IN').count()
    #total visits today
    today = date.today()
    total_visits_today = record.objects.filter(date=today).count()
    message=""
    x=False
    if request.method == 'POST':
        
        student_idx = request.POST.get('student_id')
        student_id=student_idx.upper()
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        today = date.today()
        if student_id=="" :
            try:
                student_id = readData()
            except Exception as e:
                # Handle the exception raised by readData()
                message = "Error: Failed to read data from the reader. Please try again."
                count=record.objects.filter(status='IN').count()
                total_visits_today = record.objects.filter(date=today).count()
                return render(request, 'library.html', {'form': StudentEntryExitForm(),'message':message,'x':x,'count':count,'total_visits_today':total_visits_today})
                # You may want to log the error for further investigation
                # logger.error(f"SocketError: {e}")
        
        try:
            student = record.objects.get(rollno=student_id,status='IN')
            if student.exittime is None:
                student.exittime = current_time
                student.status = 'OUT'
                student.save()
                message="Student with roll number " +student_id+" has exited the library at "+str(current_time)
                x=False
                total_visits_today = record.objects.filter(date=today).count()
                count=record.objects.filter(status='IN').count()
            else:
                    count=record.objects.filter(status='IN').count()
                    record.objects.create(rollno=student_id, entrytime=current_time,date=today)
                    message="Student with roll number "+student_id+" has entered the library at "+str(current_time)
                    x=True
                    total_visits_today = record.objects.filter(date=today).count()
                    count=record.objects.filter(status='IN').count()
        except record.DoesNotExist:
            
            record.objects.create(rollno=student_id, entrytime=datetime.now(),date=today)
            message="Student with roll number "+student_id+" has entered the library at "+str(current_time)
            x=True
            total_visits_today = record.objects.filter(date=today).count()
            count=record.objects.filter(status='IN').count()
        
    return render(request, 'library.html', {'form': StudentEntryExitForm(),'message':message,'x':x,'count':count,'total_visits_today':total_visits_today})

def records_today(request):
    today = date.today()
    students = record.objects.filter(date=today).order_by('-entrytime')
    return render(request, 'records_today.html', {'students': students})



#show all records
def allrecords(request):
    students = record.objects.all().order_by('-entrytime')
    form = DateForm(request.POST)
    return render(request, 'allrecords.html', {'students': students, 'form': form})

# view to display records of a particular date
def records(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        
        students = record.objects.filter(date=date)
        return render(request, 'records.html', {'students': students, 'form': DateForm(),'date': date})
    return render(request, 'records_form.html', {'form': DateForm()})

# view to display records of a particular month
def recordsbymonth(request):
    if request.method == 'POST':
        month = request.POST.get('month')
        monthname = datetime.strptime(month, '%Y-%m-%d').strftime('%B')
        month = int(month[5:7])
        students = record.objects.filter(date__month=month)
        return render(request, 'records_month.html', {'students': students, 'form': MonthForm,'month': month, 'monthname': monthname})
    return render(request, 'records_month_form.html', {'form': MonthForm()})


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

# view to export records of a particular month to csv
def exportbymonth(request):
    if request.method == 'POST':
        month = request.POST.get('month')
        month = int(month[5:7])
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['Roll No', 'Entry Time', 'Exit Time', 'Date'])
        for row in record.objects.filter(date__month=month).values_list('rollno', 'entrytime', 'exittime'):
            writer.writerow(row)
        response['Content-Disposition'] = 'attachment; filename="records.csv"'
        return response
    else:
        return render(request, 'records_month_formcsv.html', {'form': MonthForm()})
    

def readData():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.SOL_TCP)
		s.connect((readerIP, readerPort))
	except:
		raise Exception('NetworkError: Socket creation failed.')

	#print("Sending Read request.")
	cmd = bytearray([10, 255, 2, 128, 117])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)
	cnt = out[5]
	#print("Response: " + " ".join("%02x" % b for b in out))

	#print("Sending get tag data request.")
	cmd = bytearray([10, 255, 3, 65, 16, 163])
	s.send(cmd)

	# Reading response
	out = s.recv(2048)
	#print("Response: " + " ".join("%02x" % b for b in out))
	if out[4] > 1:
		raise Exception("WARNING: More than one tags in range!!!")
	elif out[4] == 0:
		raise Exception("WARNING: No tags in range!!!")
	out = out[7:7+12][::-1]
	if out[1] == 0x9e:
		raise Exception("WARNING: Attempted to read empty tag.")
	out = out.decode()
	out = ''.join([c if ord(c) != 0 else '' for c in out])

	
	return out

