import csv
import os
import django
from datetime import datetime, timedelta, date

def mark_exit():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entryexit.settings')
    django.setup()

    from enter.models import record

    #exit all the duplicate entries in the status_in_duplicates.csv file
    with open('status_in_duplicates.csv', mode='r') as file:
        reader = csv.reader(file)
        for row in reader:
            #there are multiple entries for this roll number
            #exit the entries that are IN
            entries_to_update = record.objects.filter(rollno=row[0], status='IN')
            for entry in entries_to_update:
                entry.exittime = "23:59:59"
                entry.status = 'OUT'
                entry.save()
                

    

if __name__ == "__main__":
    mark_exit()