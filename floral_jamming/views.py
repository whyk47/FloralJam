import json
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required
from datetime import datetime

from .models import *
from .forms import *

GUEST = User.objects.get(username="guest")

@staff_member_required
def create(request):
     if request.method == "POST":
          event_form = EventForm(request.POST)
          if event_form.is_valid():
               event = event_form.save(commit=False)
               event.creator = request.user
               event.save()
               return HttpResponseRedirect(reverse("floral_jamming:index"))
          else:
               return render(request, "floral_jamming/create.html", {
                    "form": event_form
               })
     else:
          return render(request, "floral_jamming/create.html", {
               "form": EventForm()
          })

def index(request):
     user = request.user
     if user.is_staff:
          events = Event.objects.filter(creator__username=user.username, time__gte=datetime.now()).order_by('time')
     else:
          events = Event.objects.filter(time__gte=datetime.now()).order_by('time')
     return render(request, 'floral_jamming/index.html', {
          'user': user,
          'is_staff': user.is_staff,
          'events': events
     })

def sign_up(request, event_id: int):
     event = Event.objects.get(id=event_id)
     if request.user.is_authenticated:
          user = User.objects.get(id=request.user.id)
          attendee = Attendee(user=user, event=event, email=user.email, first_name=user.first_name, last_name=user.last_name)
          attendee.save()
          # TODO handle user sign up
          return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
     else:
          if request.method == "POST":
               attendee_form = AttendeeForm(request.POST) 
               if attendee_form.is_valid():
                    attendee = attendee_form.save(commit=False)
                    attendee.event = event
                    attendee.user = GUEST
                    attendee.save()
                    return HttpResponse('TODO')
               else:
                    return render(request, 'floral_jamming/sign_up.html', {
                         'event': event,
                         'form': attendee_form,
                         'message': attendee_form.errors
                    })
          else:
               return render(request, 'floral_jamming/sign_up.html', {
                    'event': event,
                    'form': AttendeeForm(),
               })
          
def cancel_sign_up(request, event_id: int):
     event = Event.objects.get(id=event_id)
     if request.user.is_authenticated:
          user = User.objects.get(id=request.user.id)
          attendee = Attendee.objects.get(event=event, user=user)
          attendee.delete()
     return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))

def details(request, event_id: int):
     event = Event.objects.get(id=event_id)
     user = User.objects.get(id=request.user.id) if request.user.is_authenticated else None
     attendee = None
     if request.method == "POST":
          if user:
               attendee, created = Attendee.objects.update_or_create(
                    event=event, 
                    user=user,
                    defaults={
                         'pax': int(request.POST['pax']),
                         'email': user.email,
                         'first_name': user.first_name,
                         'last_name': user.last_name
                    }
               )
          else:
               form = AttendeeForm(request.POST)
               assert 'guest_id' in request.POST
               guest_id = request.POST['guest_id']
               if form.is_valid():
                    attendee, created = Attendee.objects.update_or_create(
                         event=event, 
                         guest_id=guest_id, 
                         user=GUEST, 
                         defaults={**form.cleaned_data}
                    )
               else:
                    return render(request, 'floral_jamming/sign_up.html', {
                         'event': event,
                         'form': form,
                         'message': form.errors
                    })
     
     return render(request, 'floral_jamming/details.html', {
          'event': event,
          'attendee': attendee,
          'form': AttendeeForm(),
     })

def login_view(request, event_id: int = 0):
     if request.user.is_authenticated:
          return HttpResponseRedirect(reverse("floral_jamming:index"))
     if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            if event_id > 0:
                return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
            return HttpResponseRedirect(reverse("floral_jamming:index"))
        else:
            return render(request, "floral_jamming/login.html", {
                "message": "Invalid username and/or password.",
                "event_id": event_id
            })
     else:
          return render(request, "floral_jamming/login.html", {
               "event_id": event_id
          })
     

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("floral_jamming:index"))


def register(request, event_id: int = 0):
     if request.user.is_authenticated:
          return HttpResponseRedirect(reverse("floral_jamming:index"))
     if request.method == "POST":
          form = UserForm(request.POST)
          if form.is_valid():
               data = form.cleaned_data

               # Ensure password matches confirmation
               password = data["password"]
               confirmation = request.POST["confirmation"]
               if password != confirmation:
                    return render(request, "floral_jamming/register.html", {
                         "message": "Passwords must match.",
                         "event_id": event_id
                    })

               # Attempt to create new user
               try:
                    data.pop('confirmation')
                    user = User.objects.create_user(**data)
                    user.save()
               except IntegrityError:
                    return render(request, "floral_jamming/register.html", {
                         "message": "Username already taken.",
                         "event_id": event_id
                    })
               login(request, user)
               if event_id > 0:
                    return HttpResponseRedirect(reverse("floral_jamming:details", args=[event_id]))
               return HttpResponseRedirect(reverse("floral_jamming:index"))
          else:
               return render(request, "floral_jamming/register.html", {
                         "message": form.errors,
                         "event_id": event_id
                    })
     else:
          return render(request, "floral_jamming/register.html", {
               "form": UserForm(),
               "event_id": event_id,
          })