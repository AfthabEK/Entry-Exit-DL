
from django.contrib import admin
from django.urls import include, path
from enter import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.library, name='library'),
    path('/', views.library, name='library'),
    path('home', views.library, name='library'),
    path('home/', views.library, name='library'),
    path('library', views.library, name='library'),
    path('library/', views.library, name='library'),
    path('records/', views.records, name='records'),
    path('allrecords/', views.allrecords, name='allrecords'),
    path('recordsbystatus/', views.recordsbystatus, name='recordsbystatus'),
    path('export/', views.export, name='export'),
    path('exportbydate/', views.exportbydate, name='exportbydate'),
    path('recordsbymonth/', views.recordsbymonth, name='recordsbymonth'),
    path('exportbymonth/', views.exportbymonth, name='exportbymonth')
]
