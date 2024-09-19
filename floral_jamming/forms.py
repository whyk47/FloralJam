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

class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

class ForgotPasswordForm(forms.Form):
    data = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username or Email Address', 'size': 30}))

class PasswordResetForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))
    confirmation = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}))

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'time', 'location', 'description', 'capacity', 'price']
        widgets = {
            'time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows': 5}),
        }
    def __init__(self, *args, **kwargs):
        super(EventForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = True
            field.widget.attrs['placeholder'] = field_name.capitalize()
            field.label = ''
        self.fields['price'].widget.attrs['placeholder'] = 'Price ($)'
        self.fields['price'].widget.attrs['min'] = 0
        self.fields['capacity'].widget.attrs['min'] = 0


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
    
        
