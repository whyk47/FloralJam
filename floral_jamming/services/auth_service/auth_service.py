from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from guest_user.functions import is_guest_user

from floral_jamming.services.event_service.event_service import Event_Service
from ...models import User
from ...forms import UserForm
from .auth_service_exceptions import *


class Auth_Service(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Auth_Service, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.event_service = Event_Service()

    def is_authenticated_user(self, user: User) -> bool:
        return user.is_authenticated and not is_guest_user(user)
    
    def is_anonymous_user(self, user: User) -> bool:
        return user.is_anonymous
    
    def is_staff_user(self, user: User) -> bool:
        return user.is_staff
    
    def is_guest_user(self, user: User) -> bool:
        return is_guest_user(user)
    
    def convert_guest(self, user: User) -> None:
        if not self.is_guest_user(user):
            return
        attendees = self.event_service.get_user_attendees(user)
        for attendee in attendees:
            attendee.user = user
            attendee.save()

    def update_user_details(self, data: dict, user: User) -> None:
        user.first_name = data['first_name']
        user.last_name = data['last_name']
        user.email = data['email']
        user.save()
        
    def login(self, request: HttpRequest, username: str, password: str) -> None:
        if self.is_authenticated_user(request.user):
            raise User_Already_Logged_In('User already logged in')
        user = authenticate(username=username, password=password)
        if not user:
            raise Invaild_Credentials('Invalid credentials')
        self.convert_guest(user)
        login(request, user)
    
    def logout(self, request: HttpRequest) -> None:
        if not self.is_authenticated_user(request.user):
            raise User_Not_Logged_In('User not logged in')
        logout(request)

    def register(self, request: HttpRequest, form: UserForm) -> None:
        if self.is_authenticated_user(request.user):
            raise User_Already_Logged_In('User already logged in')
        if form.is_valid():
            data = form.cleaned_data
            if data['password'] != data['confirmation']:
                raise Invalid_Form('Passwords do not match')
            if User.objects.filter(username=data['username']).exists():
                raise Invalid_Form('Username already taken')
            user = form.save()
            self.convert_guest(request, user)
            login(request, user)
        else:
            raise Invalid_Form(form.errors)
        
