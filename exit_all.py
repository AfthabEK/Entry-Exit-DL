
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entryexit.settings')
django.setup()

from enter.models import record  # Replace 'your_app' with your actual Django app name

def exit_all():
    try:
        # Get all records from the database which are currently in
        all_entries = record.objects.filter(exittime__isnull=True)
        
        #find number of entries
        entry_count = len(all_entries)

        # a confirmation message to delete the invalid entries
        if entry_count > 0:
            print(f"There are {entry_count} entries.")
            confirm = input("Do you want to exit them? (yes/no): ").lower()
            if confirm == "yes":
                for entry in all_entries:
                    print(f"Exiting entry: {entry}")
                    entry.delete()
            else:
                print("Exit canceled.")
        else:
            print("No entries found.")


        # Delete the invalid entries
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    exit_all()
    
