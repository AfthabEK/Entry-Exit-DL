from django.db import models

class record(models.Model):
    rollno = models.CharField(max_length=100)
    entrytime = models.DateTimeField()
    exittime = models.DateTimeField(blank=True, null=True)
    status=models.CharField(default='IN',max_length=4)

    def __str__(self):
        return self.rollno

