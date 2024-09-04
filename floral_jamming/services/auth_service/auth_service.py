from django.contrib.auth import authenticate, login, logout
from django.http import HttpRequest
from guest_user.functions import is_guest_user

from ...util import get_data, Invalid_Form
from ...models import User
from ...forms import LoginForm, PasswordResetForm, ForgotPasswordForm, UserForm
from .auth_service_exceptions import *
from ..email_service.email_service import Email_Service


# TODO: Add alternative signin methods

class Auth_Service(object):
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Auth_Service, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self._email_service = Email_Service()
    
    @property
    def __email_service(self):
        return self._email_service
        
    @staticmethod
    def is_authenticated_user(user: User) -> bool:
        return user.is_authenticated and not is_guest_user(user) and user.is_email_verified
    
    @staticmethod
    def is_anonymous_user(user: User) -> bool:
        return user.is_anonymous
    
    @staticmethod
    def is_staff_user(user: User) -> bool:
        return user.is_staff
    
    @staticmethod
    def is_guest_user(user: User) -> bool:
        return is_guest_user(user)
    
    @staticmethod
    def is_email_verified(user: User) -> bool:
        return user.is_email_verified
        
    def get_user_by_username(self, username: str) -> User:
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            raise Invaild_Credentials("Invalid credentials")
        
    def get_user_by_email(self, email: str) -> User:
        users = User.objects.filter(email=email)
        for user in users:
            if self.is_authenticated_user(user):
                return user
        raise Invaild_Credentials("Invalid credentials")
    
    def get_user_by_id(self, user_id: int) -> User:
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise User_Does_Not_Exist("The user does not exist")
    
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
        if data['email'] != user.email:
            user.is_email_verified = False
            user.email = data['email']
        user.save()

    def login(self, request: HttpRequest, form: LoginForm) -> None:
        if self.is_authenticated_user(request.user):
            raise User_Already_Logged_In('User already logged in')
        data = get_data(form, Invaild_Credentials, 'Invalid credentials')
        username=data['username']
        user = authenticate(username=username, password=data['password'])
        if not user:
            inactive_user = self.get_user_by_username(username)
            if not self.is_email_verified(inactive_user):
                raise User_Email_Not_Verified(inactive_user.id)
            raise Invaild_Credentials('Invalid credentials')
        self.login_user(request, user)

    def login_user(self, request: HttpRequest, user: User) -> None:
        self.__convert_guest(request.user, user)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    
    def logout(self, request: HttpRequest) -> None:
        if not self.is_authenticated_user(request.user):
            raise User_Not_Logged_In('User not logged in')
        logout(request)

    def __validate_registration_data(self, data: dict) -> dict:
        if data['password'] != data['confirmation']:
            raise Invalid_Form('Passwords do not match')
        if User.objects.filter(username=data['username']).exists():
            raise Invalid_Form('Username already taken')
        data.pop('confirmation')
        return data

    def register(self, request: HttpRequest, form: UserForm) -> User:
        if self.is_authenticated_user(request.user):
            raise User_Already_Logged_In('User already logged in')
        data = self.__validate_registration_data(get_data(form))
        new_user = User.objects.create_user(**data)
        if self.is_email_verified(request.user) and request.user.email == new_user.email:
            self.set_email_verified(new_user)
        else:
            new_user.is_active = False
        new_user.save()
        return new_user
        
    def set_email_verified(self, user: User) -> None:
        # ! incomplete implementation. use event_service.set_email_verified instead
        user.is_active = True
        user.is_email_verified = True
        user.save()
        self.__email_service.delete_tokens(user)

    def request_password_reset(self, form: ForgotPasswordForm) -> User:
        data = get_data(form)
        try:
            user = self.get_user_by_username(data['data'])
        except Invaild_Credentials as e:
            user = self.get_user_by_email(data['data'])
        if not self.is_authenticated_user(user):
            raise Invaild_Credentials('Invalid credentials')
        return user

    def reset_password(self, user: User, form: PasswordResetForm) -> None:
        if not self.is_authenticated_user(user):
            raise Invaild_Credentials('Invalid credentials')
        data = get_data(form)
        if data['password'] != data['confirmation']:
            raise Invalid_Form("Passwords do not match")
        user.set_password(data['password'])
        user.save()
        self.__email_service.delete_tokens(user)