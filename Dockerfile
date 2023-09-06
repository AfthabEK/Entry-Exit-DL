# Use the official Python image as the base image
FROM python:3.11-slim-bookworm

# Set the working directory in the container
WORKDIR /app

# Copy your Django app files into the container
COPY . /app/

# Install dependencies (if you have a requirements.txt file)
RUN pip install -r requirements.txt
RUN python manage.py migrate
# Expose the port your Django app will run on (default is 8000)
EXPOSE 8000

# Start your Django app
CMD ["python", "manage.py", "runserver","0.0.0.0:8000" ]

