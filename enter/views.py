import datetime,csv
from django.shortcuts import render
from .models import record
from .models import student as studentrec
from .forms import StudentEntryExitForm, DateForm, MonthForm
from datetime import datetime
from django.shortcuts import redirect
from datetime import date, timedelta
from django.http import HttpResponse
import socket
import time

readerIP='192.168.230.16'
readerPort=100


def library(request):
    # Get the current date and yesterday's date
    today = date.today()
    yesterday = datetime.now().date() - timedelta(days=2)

    # Update entries with status 'IN' and date before or equal to yesterday
    record.objects.filter(status='IN', date__lte=yesterday, exittime__isnull=True).update(exittime='23:30:00', status='OUT')


    # Count the number of students with 'IN' status for today
    count = record.objects.filter(status='IN', date=today).count()

    # Count total visits today
    total_visits_today = record.objects.filter(date=today).count()

    message = ""
    x = False

    # Separate counts for different shifts
    morning = record.objects.filter(entrytime__gte='00:00:00', entrytime__lte='08:00:00', date=today).count()
    general = record.objects.filter(entrytime__gte='08:00:00', entrytime__lte='16:30:00', date=today).count()
    night = record.objects.filter(entrytime__gte='16:30:00', entrytime__lte='23:59:59', date=today).count()

    if request.method == 'POST':
        student_idx = request.POST.get('student_id')
        student_id = student_idx.upper()
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")

        if student_id == "":
            student_id = read_data_with_retry()
            if student_id is None:
                message = "Error: Failed to read data from the reader. Please try again."
                return render(request, 'library.html', {
                    'form': StudentEntryExitForm(),
                    'message': message,
                    'x': x,
                    'count': count,
                    'total_visits_today': total_visits_today,
                    'morning_count': morning,
                    'general_count': general,
                    'night_count': night
                })
        
        try:
                # Check if student_id is in the correct format (e.g., B200719CS)
            
            if student_id==None or not( isnine(student_id) or isfour(student_id) ):
            #if student_id==None or not( len(student_id)==9 or len(student_id)==4 ) or not student_id[0].isalpha() or not student_id[1:7].isdigit() or not student_id[7:9].isalpha():
                    message = "Error: Invalid roll number format. Please try again."
            else:
                student = record.objects.get(rollno=student_id, status='IN')

                if student.exittime is None:
                    student.exittime = current_time
                    student.status = 'OUT'
                    student.save()
                    #if there is a name and rollno in the table students, change the message to the name
                    try:
                        student_name = studentrec.objects.get(rollno=student_id)
                        message = f"{student_name} has exited the library at {current_time}"
                    except:
                        if(len(student_id)==9):
                            message = f"Student with roll number {student_id} has exited the library at {current_time}"
                        else:
                            message = f"Staff with ID {student_id} has exited the library at {current_time}"
                else:
                        # Create a new record for a student entering
                    x=True
                    record.objects.create(rollno=student_id, entrytime=current_time, date=today)
                    try:
                        student_name = studentrec.objects.get(rollno=student_id)
                        message = f"{student_name} has entered the library at {current_time}"
                    except:
                        if(len(student_id)==9):
                            message = f"Student with roll number {student_id} has entered the library at {current_time}"
                        else:
                            message = f"Staff with ID {student_id} has entered the library at {current_time}"
        except record.DoesNotExist:
                # Create a new record for a student entering
            x=True
            record.objects.create(rollno=student_id, entrytime=current_time, date=today)
            try:
                student_name = studentrec.objects.get(rollno=student_id)
                message = f"{student_name} has entered the library at {current_time}"
            except:
                if(len(student_id)==9):
                    message = f"Student with roll number {student_id} has entered the library at {current_time}"
                else:
                    message = f"Staff with ID {student_id} has entered the library at {current_time}"
    return render(request, 'library.html', {
        'form': StudentEntryExitForm(),
        'message': message,
        'x': x,
        'count': count,
        'total_visits_today': total_visits_today,
        'morning_count': morning,
        'general_count': general,
        'night_count': night
    })

# view to display records of today
def records_today(request):
    today = date.today()
    students = record.objects.filter(date=today).order_by('-entrytime')
    return render(request, 'records_today.html', {'students': students})



#show all records
def allrecords(request):
    students = record.objects.all().order_by('-date','-entrytime')
    form = DateForm(request.POST)
    return render(request, 'allrecords.html', {'students': students, 'form': form})

# view to display records of a particular date
def records(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        students = record.objects.filter(date=date).order_by('-date','-entrytime')
        return render(request, 'records.html', {'students': students, 'form': DateForm(),'date': date})
    return render(request, 'records_form.html', {'form': DateForm()})

# view to display records of a particular month
def recordsbymonth(request):
    if request.method == 'POST':
        month = request.POST.get('month')
        monthname = datetime.strptime(month, '%Y-%m-%d').strftime('%B')
        year = int(month[0:4])
        month = int(month[5:7])
        students = record.objects.filter(date__month=month,date__year=year).order_by('-date','-entrytime')
        return render(request, 'records_month.html', {'students': students, 'form': MonthForm,'month': month, 'monthname': monthname, 'year': year})
    return render(request, 'records_month_form.html', {'form': MonthForm()})


# view to display records by status
def recordsbystatus(request):
        students = record.objects.filter(status='IN').order_by('-date','-entrytime')
        return render(request, 'current.html', {'students': students})

# view to export records to csv
def export(request):
    response = HttpResponse(content_type='text/csv')
    writer = csv.writer(response)
    writer.writerow(['Roll No', 'Entry Time', 'Exit Time', 'Date'])
    for row in record.objects.all().values_list('rollno', 'entrytime', 'exittime', 'date').order_by('-date','-entrytime'):
        row = list(row)  # Convert the values_list tuple to a list
        if row[1]:  # Check if entry time is not None
            row[1] = row[1].strftime('%H:%M:%S')  # Format entry time without milliseconds
        writer.writerow(row)
    response['Content-Disposition'] = 'attachment; filename="allrecords.csv"'
    return response

# view to export records of a particular date to csv
def exportbydate(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['Roll No', 'Entry Time', 'Exit Time', 'Date'])
        for row in record.objects.filter(date=date).values_list('rollno', 'entrytime', 'exittime','date').order_by('-date','-entrytime'):
            writer.writerow(row)
        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(date)
        return response
    else:
        return render(request, 'records_formcsv.html', {'form': DateForm()})

# view to export records of a particular month to csv
def exportbymonth(request):
    if request.method == 'POST':
        date = request.POST.get('month')
        
        year=date[0:4]
        month = int(date[5:7])
        monthname = datetime.strptime(date, '%Y-%m-%d').strftime('%B')
        yearname=str(year)
        response = HttpResponse(content_type='text/csv')
        writer = csv.writer(response)
        writer.writerow(['Roll No', 'Entry Time', 'Exit Time', 'Date'])
        for row in record.objects.filter(date__month=month,date__year=year).values_list('rollno', 'entrytime', 'exittime', 'date').order_by('-date','-entrytime'):
            writer.writerow(row)
        response['Content-Disposition'] = 'attachment; filename="{0}.csv"'.format(monthname+' '+yearname)
        return response
    else:
        return render(request, 'records_month_formcsv.html', {'form': MonthForm()})
    


def read_data_with_retry():
    start_time = time.time()
    while time.time() - start_time < 5:
        try:
            student_id = readData()
            if student_id:
                return student_id[1:]  # Return the data if successfully read
        except Exception as e:
            pass
    return None  

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


def shifts(request):
    if request.method == 'GET':
        morning = record.objects.filter(entrytime__gte='00:00:00', entrytime__lte='08:00:00').count()
        general = record.objects.filter(entrytime__gte='08:00:00', entrytime__lte='16:30:00').count()
        night = record.objects.filter(entrytime__gte='16:30:00', entrytime__lte='23:59:59').count()
        return render(request, 'shifts.html', {'morning_count': morning, 'general_count': general, 'night_count': night,'form': DateForm()})
    else:
         date = request.POST.get('date')
         morning = record.objects.filter(entrytime__gte='00:00:00', entrytime__lte='08:00:00', date=date).count()
         general = record.objects.filter(entrytime__gte='08:00:00', entrytime__lte='16:30:00', date=date).count()
         night = record.objects.filter(entrytime__gte='16:30:00', entrytime__lte='23:59:59', date=date).count()
         return render(request, 'shifts.html', {'morning_count': morning, 'general_count': general, 'night_count': night, 'date': date,'form': DateForm()})
         


def isnine(s):
    if len(s)==9 and s[0].isalpha() and s[1:7].isdigit() and s[7:9].isalpha():
        return True
    else:
        return False
    

def isfour(s):
    if len(s)==4 and s[0:3].isdigit():
        return True
    else:
        return False
