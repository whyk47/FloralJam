from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator



# Create your models here.
class User(AbstractUser):
    pass

class Session(models.Model):
    title = models.CharField(max_length=100)
    price = models.IntegerField(validators=[MinValueValidator(0)], default=80)
    time = models.DateTimeField()
    location = models.CharField(max_length=300)
    description = models.CharField(max_length=3000)
    capacity = models.IntegerField(validators=[MinValueValidator(0)], default=10)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")

    def num_attendees(self):
        return self.attendees.all().count()

class Attendee(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="attendees")
    email = models.EmailField()
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="attendees")