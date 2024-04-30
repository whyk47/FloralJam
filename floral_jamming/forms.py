from django import forms
from .models import *


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'time', 'location', 'description', 'capacity', 'price']
        widgets = {
            'time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(),
            'capacity': forms.NumberInput(attrs={'min': 0}),
            'price': forms.NumberInput(attrs={'min': 0}),
        }
        labels = {
            'price': 'Price ($)',
        }
        
