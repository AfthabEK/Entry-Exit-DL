import datetime,csv
from django.shortcuts import render
from .models import record
from .models import student as studentrec
from .forms import StudentEntryExitForm, DateForm, MonthForm
from datetime import datetime
from django.shortcuts import redirect
from datetime import date, timedelta, datetime
from django.http import HttpResponse
from .functions import isnine,isfour,read_data_with_retry
from django.db.models import Count, Q
from django.db.models.functions import ExtractWeekDay
from django.db.models import F



def library(request):
    
    # Get the current date and yesterday's date
    today = date.today()
    yesterday = datetime.now().date() - timedelta(days=2)

    # Update entries with status 'IN' and date before or equal to yesterday
    #record.objects.filter(status='IN', date__lte=yesterday, exittime__isnull=True).update(exittime='23:30:00', status='OUT')
    now = datetime.now()

    #threshold_time = datetime.now() - timedelta(hours=16)
    #students_to_update = record.objects.filter(entrytime__lt=threshold_time, exittime__isnull=True)
    #students_to_update.update(exittime=F('entrytime'), status='OUT')

    
    current_time = now.strftime("%H:%M:%S")
    #update entries with status 'IN' and time before 16 hours from now to current time
    #record.objects.filter(status='IN', entrytime__lte=(now - timedelta(minutes=1)).strftime("%H:%M:%S")).update(exittime=current_time, status='OUT')
    #record.objects.filter(status='IN', entrytime__gte=(now - timedelta(hours=16)).strftime("%H:%M:%S")).update(exittime=current_time, status='OUT')

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
            
            if student_id==None or not(isnine(student_id) or isfour(student_id) ):
            #if student_id==None or not( len(student_id)==9 or len(student_id)==4 ) or not student_id[0].isalpha() or not student_id[1:7].isdigit() or not student_id[7:9].isalpha():
                    message = "Error: Invalid roll number format. Please try again."
            else:
                student = record.objects.get(rollno=student_id, status='IN')

                if student.exittime is None:
                    student.exittime = current_time
                    student.status = 'OUT'
                    student.save()
                
                    exit_hrs, exit_mins, exit_sec = map(int, student.exittime.split(':'))
                    entry_hrs, entry_mins, entry_sec = map(int, student.entrytime.strftime("%H:%M:%S").split(':'))
                
                    # Calculate the time difference in seconds
                    time_difference_seconds = (3600 * (exit_hrs - entry_hrs) +
                                               60 * (exit_mins - entry_mins) +
                                               (exit_sec - entry_sec))
                
                    hours = time_difference_seconds // 3600
                    minutes = (time_difference_seconds % 3600) // 60
                    seconds = time_difference_seconds % 60
                
                    if minutes > 0 or seconds > 0:
                        message = f"Thank you for visiting NITC Library, you have spent {hours} Hrs {minutes} Mins {seconds} Secs here today"
                    else:
                        message = f"Thank you for visiting NITC Library, you have spent {hours} Hrs {minutes} Mins here today"
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
            # Count the number of students with 'IN' status for today
    count = record.objects.filter(status='IN', date=today).count()

    # Count total visits today
    total_visits_today = record.objects.filter(date=today).count()

    # Separate counts for different shifts
    morning = record.objects.filter(entrytime__gte='00:00:00', entrytime__lte='08:00:00', date=today).count()
    general = record.objects.filter(entrytime__gte='08:00:00', entrytime__lte='16:30:00', date=today).count()
    night = record.objects.filter(entrytime__gte='16:30:00', entrytime__lte='23:59:59', date=today).count()

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
    




def shifts(request):
    import datetime as dt 
    
    morning_start = dt.time(0, 0, 0)
    morning_end = dt.time(8, 0, 0)

    general_start = dt.time(8, 0, 0)
    general_end = dt.time(16, 30, 0)

    night_start = dt.time(16, 30, 0)
    night_end = dt.time(23, 59, 59)
    
    if request.method == 'GET':

        #count number of morning shifts with atleast one entry
        # all_entries = record.objects.all().order_by('-entrytime')
        # morning_shift_count=0
        # general_shift_count=0
        # night_shift_count=0

        # prev_date_m = None
        # prev_date_g = None
        # prev_date_n = None

        # for entry in all_entries:
        #     if entry.entrytime >= morning_start and entry.entrytime <= morning_end:
        #         if entry.date != prev_date_m:
        #             morning_shift_count += 1
        #             prev_date_m = entry.date
        #     if entry.entrytime >= general_start and entry.entrytime <= general_end:
        #         if entry.date != prev_date_g:
        #             general_shift_count += 1
        #             prev_date_g = entry.date
        #     if entry.entrytime >= night_start and entry.entrytime <= night_end:
        #         if entry.date != prev_date_n:
        #             night_shift_count += 1
        #             prev_date_n = entry.date


        # if(morning_shift_count==0):
        #     morning_shift_count=1
        # if(general_shift_count==0):
        #     general_shift_count=1
        # if(night_shift_count==0):
        #     night_shift_count=1
        morning = record.objects.filter(exittime__gte='00:00:00', exittime__lte='08:00:00').count()
        general = record.objects.filter(exittime__gte='08:00:00', exittime__lte='16:30:00').count()
        night = record.objects.filter(exittime__gte='16:30:00', exittime__lte='23:59:59').count()

        # mx=morning/morning_shift_count
        # gx=general/general_shift_count
        # nx=night/night_shift_count
        return render(request, 'shifts.html', {'morning_count': morning, 'general_count': general, 'night_count': night,
        #'morning': mx, 'general': gx, 'night': nx,
        'form': DateForm()})
    else:
        date = request.POST.get('date')
         
        # all_entries = record.objects.filter(date=date).order_by('-entrytime')
        # morning_shift_count=0
        # general_shift_count=0
        # night_shift_count=0

        # prev_date_m = None
        # prev_date_g = None
        # prev_date_n = None

        # for entry in all_entries:
        #     if entry.date != prev_date_m:
        #         if entry.entrytime >= datetime.time(0, 0, 0) and entry.entrytime <= datetime.time(8, 0, 0):
        #             morning_shift_count += 1
        #             prev_date_m = entry.date
        #     if entry.date != prev_date_g:
        #         if entry.entrytime >= datetime.time(8, 0, 0) and entry.entrytime <= datetime.time(16, 30, 0):
        #             general_shift_count += 1
        #             prev_date_g = entry.date
        #     if entry.date != prev_date_n:
        #         if entry.entrytime >= datetime.time(16, 30, 0) and entry.entrytime <= datetime.time(23, 59, 59):
        #             night_shift_count += 1
        #             prev_date_n = entry.date

        # if(morning_shift_count==0):
        #     morning_shift_count=1
        # if(general_shift_count==0):
        #     general_shift_count=1
        # if(night_shift_count==0):
        #     night_shift_count=1

        

        morning = record.objects.filter(exittime__gte='00:00:00', exittime__lte='08:00:00', date=date).count()
        general = record.objects.filter(exittime__gte='08:00:00', exittime__lte='16:30:00', date=date).count()
        night = record.objects.filter(exittime__gte='16:30:00', exittime__lte='23:59:59', date=date).count()

        # mx=morning/morning_shift_count
        # gx=general/general_shift_count
        # nx=night/night_shift_count
        return render(request, 'shifts.html', {'morning_count': morning, 'general_count': general, 'night_count': night,
        # 'morning': mx, 'general': gx, 'night': nx,
        'date': date,'form': DateForm()})
         



def statistics(request):

    monday=0;
    tuesday=0;
    wednesday=0;
    thursday=0;
    friday=0;
    saturday=0;
    sunday=0;

    monday_entries=0;
    tuesday_entries=0;
    wednesday_entries=0;
    thursday_entries=0;
    friday_entries=0;
    saturday_entries=0;
    sunday_entries=0;


    # Query the database for all entry records  
    all_entries = record.objects.all().order_by('-date')

    # Iterate through the entries and update the dictionaries
    prev_date = None
    for entry in all_entries:
        if entry.date != prev_date:
            if entry.date.strftime("%A")=="Monday":
                monday+=1
            elif entry.date.strftime("%A")=="Tuesday":
                tuesday+=1
            elif entry.date.strftime("%A")=="Wednesday":
                wednesday+=1
            elif entry.date.strftime("%A")=="Thursday":
                thursday+=1
            elif entry.date.strftime("%A")=="Friday":
                friday+=1
            elif entry.date.strftime("%A")=="Saturday":
                saturday+=1
            elif entry.date.strftime("%A")=="Sunday":
                sunday+=1
            prev_date = entry.date
        if entry.status=="OUT":
            if entry.date.strftime("%A")=="Monday":
                monday_entries+=1
            elif entry.date.strftime("%A")=="Tuesday":
                tuesday_entries+=1
            elif entry.date.strftime("%A")=="Wednesday":
                wednesday_entries+=1
            elif entry.date.strftime("%A")=="Thursday":
                thursday_entries+=1
            elif entry.date.strftime("%A")=="Friday":
                friday_entries+=1
            elif entry.date.strftime("%A")=="Saturday":
                saturday_entries+=1
            elif entry.date.strftime("%A")=="Sunday":
                sunday_entries+=1


    if(monday==0):
        monday=1
    if(tuesday==0):
        tuesday=1
    if(wednesday==0):
        wednesday=1
    if(thursday==0):
        thursday=1
    if(friday==0):
        friday=1
    if(saturday==0):
        saturday=1
    if(sunday==0):
        sunday=1

    #return render(request, "statistics.html", {'monday':monday,'tuesday':2,'wednesday':3,'thursday':4,'friday':5,'saturday':6,'sunday':7})
    #return render(request, "statistics.html", {'monday':monday,'tuesday':tuesday,'wednesday':wednesday,'thursday':thursday,'friday':friday,'saturday':saturday,'sunday':sunday,'monday_entries':monday_entries,'tuesday_entries':tuesday_entries,'wednesday_entries':wednesday_entries,'thursday_entries':thursday_entries,'friday_entries':friday_entries,'saturday_entries':saturday_entries,'sunday_entries':sunday_entries})
    return render(request, "statistics.html", {'monday':monday_entries/monday,
    'tuesday':tuesday_entries/tuesday,
    'wednesday':wednesday_entries/wednesday,
    'thursday':thursday_entries/thursday,
    'friday':friday_entries/friday,
    'saturday':saturday_entries/saturday,
    'sunday':sunday_entries/sunday,
        })
