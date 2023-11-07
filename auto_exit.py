import os
import django
from datetime import datetime, timedelta, date

def mark_exit():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entryexit.settings')
    django.setup()
    yesterday = date.today() - timedelta(days=2)

    from enter.models import record

    try:
        #Collect all entries that are IN
        entries_to_update = record.objects.filter(status='IN', date=yesterday)
        #Store their roll numbers in a list
        roll_numbers = []
        for entry in entries_to_update:
            roll_numbers.append(entry.rollno)


        # Mark them as out at 23:59:59
        for entry in entries_to_update:
            entry.exittime = entry.exittime if entry.exittime else "23:59:59"
            entry.status = 'OUT'
            entry.save()
        
        #Mark them as in at 00:00:00
        for roll_number in roll_numbers:
            entry = record.objects.create(rollno=roll_number, date=date.today(), entrytime="00:01:00", status='IN')
            entry.save()

        return True


        

    except Exception as e:
        # You may want to log the error for further investigation
        # logger.error(f"Error occurred: {e}")
        print(e)
        return False

if __name__ == "__main__":
    success = mark_exit()
    if success:
        print("Entries have been updated.")
    else:
        print("Error occurred while updating entries.")
