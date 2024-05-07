from uuid import uuid4
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .custom_user import User


class Event(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField(validators=[MinValueValidator(0)], default=80)
    time = models.DateTimeField()
    location = models.CharField(max_length=300)
    description = models.CharField(max_length=3000)
    capacity = models.IntegerField(validators=[MinValueValidator(0)], default=10)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")

    def num_attendees(self) -> int:
        return sum([attendee.pax for attendee in self.attendees.all()])
    
    def remaining_slots(self) -> int:
        return self.capacity - self.num_attendees()

class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendees", null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendees")
    pax = models.IntegerField(validators=[MinValueValidator(1)])

class EmailConfirmationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")