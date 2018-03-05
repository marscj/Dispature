from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from main.models import Staff,Task

class TaskForm(forms.Form):
    start_time = forms.DateTimeField()
    end_time = forms.DateTimeField()    
