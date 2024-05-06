from datetime import datetime
from typing import *
from django.db.models.query import QuerySet

from .event_service_exceptions import *
from ..auth_service.auth_service import Auth_Service
from ...models import User, Event, Attendee
from ...forms import AttendeeForm, EventForm, GuestForm


class Event_Service:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Event_Service, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self.auth_service = Auth_Service()

    def create_event(self, user: User, form: EventForm) -> Event:
        auth_service = self.auth_service
        if not auth_service.is_staff_user(user):
            raise Invalid_User_Type("Must be staff user to create event")
        if form.is_valid():
            event = form.save(commit=False)
            event.creator = user
            event.save()
            return event
        else:
            raise Invalid_Form(form.errors)
        
    def get_events(self, user: User) -> Optional[QuerySet]:
        auth_service = self.auth_service
        if auth_service.is_staff_user(user):
            try:
                return user.events.filter(time__gte=datetime.now()).order_by('time')
            except Event.DoesNotExist:
                return None
        return Event.objects.filter(time__gte=datetime.now()).order_by('time')

    def get_event_by_id(self, event_id: int) -> Event:
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise Event_Does_Not_Exist()
        
    def get_attendee(self, user: User, event: Event) -> Optional[Attendee]:
        auth_service = self.auth_service
        if auth_service.is_anonymous_user(user):
            return None
        return event.attendees.filter(user=user).first()
    
    def get_user_attendees(self, user: User) -> QuerySet:
        return user.attendees.all()
    
    def create_or_update_user_attendee(self, user: User, event: Event, pax: int) -> Attendee:
        if not self.auth_service.is_authenticated_user(user):
            raise Invalid_User_Type("Must be authenticated user")
        if pax > event.remaining_slots():
            raise Invalid_Form("Number of pax exceeds capacity of event")
        attendee, created = event.attendees.update_or_create(user=user, defaults={'pax': pax})
        return attendee
    
    def create_or_update_guest_attendee(self, user: User, event: Event, attendee_form: AttendeeForm, guest_form: GuestForm) -> Attendee:
        if not self.auth_service.is_guest_user(user):
            raise Invalid_User_Type("Must be guest user")
        if attendee_form.is_valid() and guest_form.is_valid():
            attendee_data, guest_data = attendee_form.cleaned_data, guest_form.cleaned_data
            if attendee_data['pax'] > event.remaining_slots():
                raise Invalid_Form("Number of pax exceeds capacity of event")
            self.auth_service.update_user_details(guest_data, user)
            attendee, created = event.attendees.update_or_create(user=user, defaults={**attendee_data})
        else:
            raise Invalid_Form(attendee_form.errors)
        return attendee
    
    def delete_attendee(self, user: User, event: Event) -> None:
        auth_service = self.auth_service
        if auth_service.is_anonymous_user(user):
            raise Invalid_User_Type("Must be authenticated or guest user")
        attendee = self.get_attendee(user, event)
        if not attendee:
            raise Attendee_Does_Not_Exist("Attendee does not exist")
        attendee.delete()

    


    