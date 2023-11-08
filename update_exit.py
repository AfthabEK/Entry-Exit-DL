import os
import django
from datetime import datetime, timedelta

def update_entries():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entryexit.settings')
    django.setup()

    from enter.models import record

    try:
        yesterday = datetime.now().date() - timedelta(days=2)
        
        entries_to_update = record.objects.filter(status='IN', date__lte=yesterday)
        
        for entry in entries_to_update:
            entry.exittime = entry.exittime if entry.exittime else "23:30:00"
            entry.status = 'OUT'
            entry.save()

        return True
    except Exception as e:
        # You may want to log the error for further investigation
        # logger.error(f"Error occurred: {e}")
        return False

if __name__ == "__main__":
    success = update_entries()
    if success:
        print("Entries have been updated.")
    else:
        print("Error occurred while updating entries.")
