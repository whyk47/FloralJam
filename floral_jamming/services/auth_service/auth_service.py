from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from guest_user.functions import is_guest_user

from ...models import User
from ...forms import UserForm
from .auth_service_exceptions import *


class Auth_Service(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Auth_Service, cls).__new__(cls)
        return cls.instance
    
    @staticmethod
    def is_authenticated_user(user: User) -> bool:
        return user.is_authenticated and not is_guest_user(user)
    
    @staticmethod
    def is_anonymous_user(user: User) -> bool:
        return user.is_anonymous
    
    @staticmethod
    def is_staff_user(user: User) -> bool:
        return user.is_staff
    
    @staticmethod
    def is_guest_user(user: User) -> bool:
        return is_guest_user(user)
    
    def __convert_guest(self, guest: User, user: User) -> None:
        if not self.is_guest_user(guest) or guest.email != user.email:
            return
        attendees = guest.attendees.all()
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
        self.__convert_guest(request.user, user)
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
            self.__convert_guest(request.user, user)
            login(request, user)
        else:
            raise Invalid_Form(form.errors)
        
