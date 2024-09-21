from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from guest_user.decorators import allow_guest_user

from .forms import *
from .view_exceptions import *
from .util import *
from .services.auth_service.auth_service import Auth_Service
from .services.auth_service.auth_service_exceptions import *
from .services.event_service.event_service import Event_Service
from .services.event_service.event_service_exceptions import *
from .services.email_service.email_service import Email_Service
from .services.email_service.email_service_exceptions import *

auth_service = Auth_Service()
event_service = Event_Service()
email_serivce = Email_Service()

@staff_member_required
def create(request: HttpRequest, event_id: int = 0) -> HttpResponse | HttpResponseRedirect:
     try:
          event = event_service.get_event_by_id(event_id)
     except Event_Does_Not_Exist:
          event = None

     if event and request.user != event.creator:
          auth_service.logout(request)
          return HttpResponseRedirect(reverse("floral_jamming:login", args=[event_id]))
     
     if request.method == "POST":
          form = EventForm(request.POST)
          try:
               if event_id > 0:
                    event = event_service.update_event(user=request.user, event_id=event_id, form=form)
               else:
                    event = event_service.create_event(user=request.user, form=form)
               return HttpResponseRedirect(reverse("floral_jamming:details", args=[event.id]))
          except Invalid_Form as e:
               return render(request, "floral_jamming/create.html", {
                    "message": e,
                    "forms": [form],
                    "event": event,
               })
     return render(request, "floral_jamming/create.html", {
          "forms": [EventForm(instance=event)],
          "event": event,
     })

@allow_guest_user
def index(request: HttpRequest) -> HttpResponse:
     events = event_service.get_events(request.user)
     page = get_page(request, events)
     return render(request, 'floral_jamming/index/index.html', {
          'page': page,
     })

@allow_guest_user
def sign_up(request: HttpRequest, event_id: int) -> HttpResponse | HttpResponseRedirect:
     event = event_service.get_event_by_id(event_id)
     attendee = event_service.get_attendee(user=request.user, event=event)
     if request.method == "POST":
          attendee_form = AttendeeForm(request.POST)
          if auth_service.is_guest_user(request.user):
               guest_form = GuestForm(request.POST)
               try:
                    attendee = event_service.create_or_update_guest_attendee(user=request.user, event=event, attendee_form=attendee_form, guest_form=guest_form)
                    if not auth_service.is_email_verified(request.user):
                         return HttpResponseRedirect(reverse("floral_jamming:verify_email", args=[request.user.id, "email_verified", event_id]))
                    else:
                         email_serivce.send_confirmation_email(attendee, request.get_host())
               except (Invalid_Form, UNABLE_TO_SEND_EMAIL) as e:
                    return render(request, 'floral_jamming/auth/sign_up.html', {
                         'attendee': attendee,
                         'event': event,
                         'forms': [guest_form, attendee_form],
                         'message': e
                    })
               
          else:
               return HttpResponseRedirect(reverse("floral_jamming:login", args=[event_id]))
          return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
     return render(request, 'floral_jamming/auth/sign_up.html', {
          'attendee': attendee,
          'event': event,
          'forms': [GuestForm(instance=request.user), AttendeeForm(instance=attendee)]
     })

@allow_guest_user
def cancel_sign_up(request: HttpRequest, event_id: int) -> HttpResponse | HttpResponseRedirect:
     if request.method == "POST":
          event = event_service.get_event_by_id(event_id)
          event_service.delete_attendee(user=request.user, event=event)
          return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
     raise Invalid_Http_Request('Deletion must be done by POST request')

@staff_member_required
def remove_attendee(request: HttpRequest, attendee_id: int) -> HttpResponseRedirect:
     if request.method == "POST":
          # TODO send email to removed attendee
          attendee = event_service.get_attendee_by_id(attendee_id)
          event_id = attendee.event.id
          event_service.delete_attendee_by_id(attendee_id)
          return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
     raise Invalid_Http_Request('Deletion must be done by POST request')

@staff_member_required
def delete_event(request: HttpRequest, event_id: int) -> HttpResponseRedirect:
     if request.method == "POST":
          event_service.delete_event_by_id(event_id)
          return HttpResponseRedirect(reverse("floral_jamming:index"))
     raise Invalid_Http_Request('Deletion must be done by POST request')

@allow_guest_user
def details(request: HttpRequest, event_id: int) -> HttpResponse:
     event = Event.objects.get(id=event_id)
     attendee = event_service.get_attendee(user=request.user, event=event)
     attendee_form = AttendeeForm()
     msg = ''
     if request.method == "POST":
          attendee_form = AttendeeForm(request.POST)
          try:
               attendee = event_service.create_or_update_user_attendee(user=request.user, event=event, attendee_form=attendee_form)
               email_serivce.send_confirmation_email(attendee, request.get_host())
          except Invalid_Form as e:
               msg = e
     page = get_page(request, event.attendees.all())
     return render(request, 'floral_jamming/details/details.html', {
          'event': event,
          'page': page,
          'attendee': attendee,
          'forms': [attendee_form],
          'message': msg
     })

@allow_guest_user
def login_view(request: HttpRequest, event_id: int = 0) -> HttpResponse | HttpResponseRedirect:
     if auth_service.is_authenticated_user(request.user):
          return HttpResponseRedirect(reverse("floral_jamming:index"))
     if request.method == "POST":
          try:
               form = LoginForm(request.POST)
               auth_service.login(request, form)
               if event_id > 0:
                    return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
               return HttpResponseRedirect(reverse("floral_jamming:index"))
          except Invaild_Credentials as e:
               return render(request, "floral_jamming/auth/login.html", {
                    "message": e,
                    "event_id": event_id,
                    "forms": [LoginForm()],
               })
          except User_Email_Not_Verified as e:
               data = get_data(form, Invaild_Credentials, 'Invalid credentials')
               username=data['username']
               new_user = auth_service.get_user_by_username(username)
               return HttpResponseRedirect(reverse("floral_jamming:verify_email", args=[new_user.id, "email_verified", event_id]))

     return render(request, "floral_jamming/auth/login.html", {
          "event_id": event_id,
          "forms": [LoginForm()],
     })
     

@allow_guest_user
def logout_view(request: HttpRequest) -> HttpResponseRedirect:
     if not auth_service.is_authenticated_user(request.user):
          return HttpResponseRedirect(reverse("floral_jamming:index"))
     auth_service.logout(request)
     return HttpResponseRedirect(reverse("floral_jamming:index"))


@allow_guest_user
def register(request: HttpRequest, event_id: int = 0) -> HttpResponse | HttpResponseRedirect:
     if auth_service.is_authenticated_user(request.user):
          return HttpResponseRedirect(reverse("floral_jamming:index"))
     if request.method == "POST":
          try:
               form = UserForm(request.POST)
               new_user = auth_service.register(request, form)
               if auth_service.is_email_verified(new_user):
                    auth_service.login_user(request, new_user)
               return HttpResponseRedirect(reverse("floral_jamming:verify_email", args=[new_user.id, "email_verified", event_id]))
          except Invalid_Form as e:
               return render(request, "floral_jamming/auth/register.html", {
                         "message": e,
                         "event_id": event_id,
                         "forms": [form],
                    })
     return render(request, "floral_jamming/auth/register.html", {
          "forms": [UserForm()],
          "event_id": event_id,
     })
     
@allow_guest_user
def email_verified(request: HttpRequest, user_id: int, token_id: str) -> HttpResponse:
     message = None
     try:
          user = auth_service.get_user_by_id(user_id)
          if auth_service.is_authenticated_user(user):
               return render(request, "floral_jamming/auth/outcome.html", {
                    'success_message': "Your email has been verified!",
                    'user': user,
               })
          token = email_serivce.get_token_by_id(token_id)
          email_serivce.verify_email_token(user, token)
          attendees = event_service.set_email_verified(user)
          for attendee in attendees:
               email_serivce.send_confirmation_email(attendee, request.get_host())
     except (Invalid_Token, User_Does_Not_Exist) as e:
          message = e
     return render(request, "floral_jamming/auth/outcome.html", {
          'message': message,
          'success_message': "Your email has been verified!",\
          'user': user,
     })

@allow_guest_user
def verify_email(request: HttpRequest, user_id: int, path: str, event_id: int = 0) -> HttpResponse:
     message = None
     user = auth_service.get_user_by_id(user_id)
     if auth_service.is_authenticated_user(request.user):
          if event_id > 0:
               return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
          return HttpResponseRedirect(reverse("floral_jamming:index"))
     try:
          email_serivce.send_verification_email(user, path, request.get_host())
     except Too_Many_Attempts as e:
          message = e
     return render(request, "floral_jamming/auth/verify_email.html", {
          "user": user,
          "event_id": event_id,
          "message": message,
     })

@allow_guest_user
def forgot_password(request: HttpRequest, event_id: int = 0) -> HttpResponse | HttpResponseRedirect:
     message = None
     if request.method == "POST":
          form = ForgotPasswordForm(request.POST)
          try:
               user = auth_service.request_password_reset(form)
               return HttpResponseRedirect(reverse("floral_jamming:verify_email", args=[user.id, "reset_password", event_id]))
          except (Invalid_Form, Invaild_Credentials) as e:
               message = e
     return render(request, "floral_jamming/auth/forgot_password.html", {
          "message": message,
          "forms": [ForgotPasswordForm()],
          "event_id": event_id,
     })


@allow_guest_user
def reset_password(request: HttpRequest, user_id: int, token_id: str) -> HttpResponse:
     message = None
     form = PasswordResetForm()
     try:
          user = auth_service.get_user_by_id(user_id)
          if not auth_service.is_authenticated_user(user):
               raise Invaild_Credentials('Invalid credentials')
          token = email_serivce.get_token_by_id(token_id)
          email_serivce.verify_email_token(user, token)
     except (Invalid_Token, User_Does_Not_Exist, Invaild_Credentials) as e:
          return render(request, "floral_jamming/auth/outcome.html", {
               "message": e
          })
     if request.method == "POST":
          form = PasswordResetForm(request.POST)
          try:
               auth_service.reset_password(user, form)
               return render(request, "floral_jamming/auth/outcome.html", {
                    "success_message": "Your Password has been reset!",
                    "user": user,
               })
          except Invalid_Form as e:
               message = e
     return render(request, "floral_jamming/auth/reset_password.html", {
          "forms": [form],
          "user_id": user_id,
          "token_id": token_id,
          "message": message,
     })
