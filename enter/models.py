from django.db import models

class record(models.Model):
    rollno = models.CharField(max_length=100)
    entrytime = models.TimeField(auto_now_add=True)
    exittime = models.TimeField(auto_now_add=False, null=True, blank=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.rollno

class Student(models.Model):
    roll_number = models.CharField(max_length=10)
    entry_time = models.DateTimeField(blank=True, null=True)
    exit_time = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.roll_number