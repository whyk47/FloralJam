from floral_jamming.models import Attendee, User
from guest_user.models import Guest
from guest_user.functions import is_guest_user



def convert_guest(guest: Guest, user: User) -> None:
    attendees = Attendee.objects.filter(guest=guest)
    for attendee in attendees:
        attendee.user = user
        attendee.save()

def is_authenticated_user(user) -> bool:
    return user.is_authenticated and not is_guest_user(user)