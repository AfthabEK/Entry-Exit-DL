import os
import django

def delete_entries_starting_with(prefix):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entryexit.settings')
    django.setup()

    from enter.models import record

    try:
        # Get the count of entries starting with the provided prefix
        entry_count = record.objects.filter(rollno__startswith=prefix).count()

        if entry_count > 0:
            print(f"There are {entry_count} entries that start with '{prefix}'.")
            confirm = input("Do you want to delete them? (yes/no): ").lower()
            if confirm == "yes":
                bad_entries = record.objects.filter(rollno__startswith=prefix)
                bad_entries.delete()
                return True
            else:
                print("Deletion canceled.")
                return False
        else:
            print(f"No entries found that start with '{prefix}'.")
            return False
    except Exception as e:
        # You may want to log the error for further investigation
        # logger.error(f"Error occurred: {e}")
        return False

if __name__ == "__main__":
    prefix_to_delete = input("Enter the prefix to search and delete: ")
    success = delete_entries_starting_with(prefix_to_delete)
    if success:
        print("Entries have been deleted.")
    else:
        print("Error occurred while processing entries.")
