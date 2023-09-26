from django.db import models

class record(models.Model):
    rollno = models.CharField(max_length=100)
    entrytime = models.TimeField()
    exittime = models.TimeField(blank=True, null=True)
    date = models.DateField()
    status=models.CharField(default='IN',max_length=4)

    def __str__(self):
        return self.rollno


class student(models.Model):
    rollno = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    def __str__(self):
        return self.name
