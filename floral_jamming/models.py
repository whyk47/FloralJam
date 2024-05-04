from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid


# Create your models here.
class User(AbstractUser):
    pass

class Event(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField(validators=[MinValueValidator(0)], default=80)
    time = models.DateTimeField()
    location = models.CharField(max_length=300)
    description = models.CharField(max_length=3000)
    capacity = models.IntegerField(validators=[MinValueValidator(0)], default=10)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")

    def num_attendees(self):
        return sum([attendee.pax for attendee in self.attendees.all()])
    
    def remaining_slots(self):
        return self.capacity - self.num_attendees()

class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendees", default=None)
    guest_id = models.UUIDField(null=True)
    email = models.EmailField()
    first_name = models.CharField(max_length=100, default="")
    last_name = models.CharField(max_length=100, default="")
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendees")
    pax = models.IntegerField(validators=[MinValueValidator(1)])