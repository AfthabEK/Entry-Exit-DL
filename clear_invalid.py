
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entryexit.settings')
django.setup()

from enter.models import record  # Replace 'your_app' with your actual Django app name

def delete_invalid_entries():
    try:
        # Get all records from the database
        all_entries = record.objects.all()




        # Filter invalid entries (roll number length not equal to 9)
        invalid_entries = [entry for entry in all_entries if len(entry.rollno) != 9]
        #find number of invalid entries
        entry_count = len(invalid_entries)

        # a confirmation message to delete the invalid entries
        if entry_count > 0:
            print(f"There are {entry_count} invalid entries.")
            confirm = input("Do you want to delete them? (yes/no): ").lower()
            if confirm == "yes":
                for entry in invalid_entries:
                    print(f"Deleting invalid entry: {entry}")
                    entry.delete()
            else:
                print("Deletion canceled.")
        else:
            print("No invalid entries found.")


        # Delete the invalid entries
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    delete_invalid_entries()
