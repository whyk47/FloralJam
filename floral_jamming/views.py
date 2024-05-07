from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from guest_user.decorators import allow_guest_user

from .forms import *
from .view_exceptions import *
from .services.auth_service.auth_service import Auth_Service
from .services.auth_service.auth_service_exceptions import *
from .services.event_service.event_service import Event_Service
from .services.event_service.event_service_exceptions import *

auth_service = Auth_Service()
event_service = Event_Service()

@staff_member_required
def create(request: HttpRequest, event_id: int = 0) -> HttpResponse | HttpResponseRedirect:
     try:
          event = event_service.get_event_by_id(event_id)
     except Event_Does_Not_Exist:
          event = None

     if request.user != event.creator:
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
                    "form": form,
                    "event": event,
               })
     else:
          return render(request, "floral_jamming/create.html", {
               "form": EventForm(instance=event),
               "event": event,
          })

@allow_guest_user
def index(request: HttpRequest) -> HttpResponse:
     return render(request, 'floral_jamming/index.html', {
          'events': event_service.get_events(request.user),
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
               except Invalid_Form as e:
                    return render(request, 'floral_jamming/sign_up.html', {
                         'attendee': attendee,
                         'event': event,
                         'attendee_form': attendee_form,
                         'guest_form': guest_form,
                         'message': e
                    })
          else:
               return HttpResponseRedirect(reverse("floral_jamming:login", args=[event_id]))
          return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
     return render(request, 'floral_jamming/sign_up.html', {
          'attendee': attendee,
          'event': event,
          'attendee_form': AttendeeForm(instance=attendee),
          'guest_form': GuestForm(instance=request.user),
     })

@allow_guest_user
def cancel_sign_up(request: HttpRequest, event_id: int) -> HttpResponse | HttpResponseRedirect:
     if request.method == "POST":
          event=event_service.get_event_by_id(event_id)
          event_service.delete_attendee(user=request.user, event=event)
          return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
     raise Invalid_Http_Request('Deletion must be done by POST request')

@allow_guest_user
def details(request: HttpRequest, event_id: int) -> HttpResponse:
     event = Event.objects.get(id=event_id)
     attendee = event_service.get_attendee(user=request.user, event=event)
     attendee_form = AttendeeForm(instance=attendee)
     msg = ''
     if request.method == "POST":
          attendee_form = AttendeeForm(request.POST)
          try:
               attendee = event_service.create_or_update_user_attendee(user=request.user, event=event, attendee_form=attendee_form)
          except Invalid_Form as e:
               msg = e
     return render(request, 'floral_jamming/details.html', {
          'event': event,
          'attendee': attendee,
          'attendee_form': attendee_form,
          'message': msg
     })

@allow_guest_user
def login_view(request: HttpRequest, event_id: int = 0) -> HttpResponse | HttpResponseRedirect:
     if auth_service.is_authenticated_user(request.user):
          return HttpResponseRedirect(reverse("floral_jamming:index"))
     if request.method == "POST":
          try:
               username = request.POST['username']
               password = request.POST['password']
               auth_service.login(request, username, password)
               if event_id > 0:
                    return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
               return HttpResponseRedirect(reverse("floral_jamming:index"))
          except Invaild_Credentials as e:
               return render(request, "floral_jamming/login.html", {
                    "message": e,
                    "event_id": event_id
               })
     else:
          return render(request, "floral_jamming/login.html", {
               "event_id": event_id
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
               auth_service.register(request, form)
               if event_id > 0:
                    return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
               return HttpResponseRedirect(reverse("floral_jamming:index"))
          except Invalid_Form as e:
               return render(request, "floral_jamming/register.html", {
                         "message": e,
                         "event_id": event_id,
                         "form": form,
                    })
     else:
          return render(request, "floral_jamming/register.html", {
               "form": UserForm(),
               "event_id": event_id,
          })

@allow_guest_user
def verify_email(request: HttpRequest, event_id: int = 0) -> HttpResponse:
     return render(request, "floral_jamming/verify_email.html", {
          "email": request.user.email,
          "event_id": event_id
     })