import os
import django

def clear_all_entries():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entryexit.settings')
    django.setup()

    from enter.models import record

    try:
        record.objects.all().delete()
        return True
    except Exception as e:
        # You may want to log the error for further investigation
        # logger.error(f"Error occurred while clearing entries: {e}")
        return False

if __name__ == "__main__":
    success = clear_all_entries()
    if success:
        print("All entries in the database have been cleared.")
    else:
        print("Error occurred while clearing entries.")
