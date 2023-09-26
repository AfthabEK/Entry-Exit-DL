import os
import django

# Set up Django's settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'entryexit.settings')
django.setup()



import csv
from django.core.wsgi import get_wsgi_application
from django.db import IntegrityError
from enter.models import student

# Set up Django's settings module

# Define a function to read and process the CSV file
def process_csv(file_path):
    # Open the CSV file
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        
        # Iterate through each row in the CSV
        for row in csv_reader:
            # Extract the desired columns (surname and cardnumber/roll number)
            student_name = row['surname']
            roll_number = row['cardnumber']

            # Create a new student object and save it to the database
            try:
                student.objects.create(name=student_name, rollno=roll_number)
            except IntegrityError as e:
                # Handle duplicate entry errors, if any
                print(f"Error: {e}")

# Example usage:
file_path = 'data.csv'
process_csv(file_path)
