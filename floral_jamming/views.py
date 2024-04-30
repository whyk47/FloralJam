from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.contrib.admin.views.decorators import staff_member_required

from .models import *
from .forms import *

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

# Create your views here.
def index(request):
     user = request.user
     if not user.is_anonymous and user.is_staff:
          events = Event.objects.filter(creator__username=user.username)
     else:
          events = Event.objects.all()
     return render(request, 'floral_jamming/index.html', {
          'user': user,
          'is_staff': user.is_staff,
          'events': events
     })

def details(request, event_id: int):
     event = Event.objects.get(id=event_id)
     return render(request, 'floral_jamming/details.html', {
          'event': event
     })

def login_view(request):
     if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("floral_jamming:index"))
        else:
            return render(request, "floral_jamming/login.html", {
                "message": "Invalid username and/or password."
            })
     else:
          return render(request, "floral_jamming/login.html")
     

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("floral_jamming:index"))


def register(request):
     if request.method == "POST":
          username = request.POST["username"]
          email = request.POST["email"]

          # Ensure password matches confirmation
          password = request.POST["password"]
          confirmation = request.POST["confirmation"]
          if password != confirmation:
               return render(request, "floral_jamming/register.html", {
                    "message": "Passwords must match."
               })

          # check for empty fields
          if not all([username, email, password, confirmation]):
               return render(request, "floral_jamming/register.html", {
                    "message": "Please fill out all fields."
               })

        # Attempt to create new user
          try:
               user = User.objects.create_user(username, email, password)
               user.save()
          except IntegrityError:
               return render(request, "floral_jamming/register.html", {
                    "message": "Username already taken."
               })
          login(request, user)
          return HttpResponseRedirect(reverse("floral_jamming:index"))
     else:
          return render(request, "floral_jamming/register.html")