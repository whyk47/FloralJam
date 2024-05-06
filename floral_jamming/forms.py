from django import forms
from .models import *


class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password']
        widgets = {
            'password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
        }
    confirmation = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

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

class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = ['pax']
        widgets = {
            'pax': forms.NumberInput(attrs={'min': 1, 'placeholder': 'Number of Pax'}),
        }

class GuestForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'email': forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
        }    
    
        
