
from django.contrib import admin
from django.urls import include, path
from enter import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('library/', views.library, name='library'),
    path('date_entries/<str:date>/', views.date_entries, name='date_entries')
    
]
