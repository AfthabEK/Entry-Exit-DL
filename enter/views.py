from django.shortcuts import render
from .models import record
from .forms import entryform
from django.views.generic import View

# Create your views here.
def home(request):
    if request.method == 'POST':
        form=entryform(request.POST)
        form.save()
        return render(request, 'home.html', {'form':entryform , 'message':'Entry Recorded'})
    else:
        return render(request, 'home.html', {'form':entryform})

def entry(request):
    return render(request, 'entry.html')
