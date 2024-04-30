from django import forms
from .models import *


class SessionForm(forms.ModelForm):
    class Meta:
        model = Session
        fields = ['title', 'time', 'location', 'description', 'capacity']
