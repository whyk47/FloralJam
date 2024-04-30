from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from .models import *
from .forms import *

GUEST = User.objects.get(username="guest")

# Create your views here.
def index(request):
     user = request.user
     if not user.is_anonymous and user.is_staff:
          sessions = Session.objects.filter(creator__username=user.username)
          return render(request, 'floral_jamming/staff.html', {
               'user': user,
               'sessions': sessions
          })
     return render(request, 'floral_jamming/index.html')

def login_view(request):
     if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        print(username, password)
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