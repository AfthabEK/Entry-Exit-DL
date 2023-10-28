import csv
import os
import django
from datetime import datetime, timedelta

def export_rollnumbers():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entryexit.settings')
    django.setup()

    from enter.models import record

    try:
        yesterday = datetime.now().date() - timedelta(days=1)
        
        entries_to_export = record.objects.filter(status='IN', date__lte=yesterday)
        
        with open('status_in.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Roll Number'])
            for entry in entries_to_export:
                writer.writerow([entry.rollno])

       
        # Sort the CSV file by roll number in ascending order
        #'''
        with open('status_in.csv', mode='r') as file:
            reader = csv.reader(file)
            sorted_rows = sorted(reader, key=lambda row: row[0])
        
        with open('status_in.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Roll Number'])
            for row in sorted_rows:
                writer.writerow(row)
                #'''

        #Export entries that occurs more than once into another csv file

        #'''

        with open('status_in_duplicates.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Roll Number'])
            for row in sorted_rows:
                if sorted_rows.count(row) > 1:
                    writer.writerow(row)

                
        
        return True
    except Exception as e:
        # You may want to log the error for further investigation
        print(f"Error occurred: {e}")
        return False
    


if __name__ == "__main__":
    success = export_rollnumbers()
    if success:
        print("Roll numbers with status IN have been exported to status_in.csv.")
    else:
        print("Error occurred while exporting roll numbers.")
