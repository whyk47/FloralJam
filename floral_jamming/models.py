from datetime import timedelta
from django.utils import timezone
from uuid import uuid4
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator

class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    
    def num_valid_tokens(self) -> int:
        for token in self.email_tokens.all():
            if token.is_expired():
                token.delete()
        return self.email_tokens.all().count()

class Event(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField(validators=[MinValueValidator(0)])
    time = models.DateTimeField()
    location = models.CharField(max_length=300)
    description = models.CharField(max_length=3000)
    capacity = models.IntegerField(validators=[MinValueValidator(0)])
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="events")

    def num_attendees(self) -> int:
        return sum([attendee.pax for attendee in self.attendees.filter(is_email_verified=True)])
    
    def remaining_slots(self) -> int:
        return self.capacity - self.num_attendees()

class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendees", null=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name="attendees")
    pax = models.IntegerField(validators=[MinValueValidator(1)])
    is_email_verified = models.BooleanField(default=False)

class EmailConfirmationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_tokens")
    
    def is_expired(self) -> bool:
        expiry = self.created_at + timedelta(hours=1)
        now = timezone.now()  
        return expiry < now