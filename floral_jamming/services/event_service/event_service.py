from datetime import datetime
from typing import *
from django.db.models.query import QuerySet

from .event_service_exceptions import *
from ..auth_service.auth_service import Auth_Service
from ...models import User, Event, Attendee
from ...forms import AttendeeForm, EventForm


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
        
    def get_events(self, user: User) -> QuerySet:
        auth_service = self.auth_service
        if auth_service.is_staff_user(user):
            return user.events.filter(time__gte=datetime.now()).order_by('time')
        return Event.objects.filter(time__gte=datetime.now()).order_by('time')

    def get_event_by_id(self, event_id: int) -> Event:
        try:
            return Event.objects.get(id=event_id)
        except Event.DoesNotExist:
            raise Event_Does_Not_Exist()
        
    def get_attendee(self, user: User, event: Event) -> Optional[Attendee]:
        auth_service = self.auth_service
        if auth_service.is_authenticated_user(user):
            return event.attendees.filter(user=user).first()
        elif auth_service.is_guest_user(user):
            return event.attendees.filter(guest=user).first()
        return None
    
    def get_user_attendees(self, user: User) -> QuerySet:
        return user.attendees.all()
    
    def create_or_update_user_attendee(self, user: User, event: Event, pax: int) -> Attendee:
        if not self.auth_service.is_authenticated_user(user):
            raise Invalid_User_Type("Must be authenticated user")
        attendee, created = event.attendees.update_or_create(user=user, defaults={'pax': pax})
        return attendee
    
    def create_or_update_guest_attendee(self, user: User, event: Event, form: AttendeeForm) -> Attendee:
        if not self.auth_service.is_guest_user(user):
            raise Invalid_User_Type("Must be guest user")
        if form.is_valid():
            data = form.cleaned_data
            self.auth_service.update_guest_details(data, user)
            attendee, created = event.attendees.update_or_create(user=user, defaults={'pax': data['pax']})
        else:
            raise Invalid_Form(form.errors)
        return attendee
    
    def delete_attendee(self, user: User, event: Event) -> None:
        auth_service = self.auth_service
        if auth_service.is_anonymous_user(user):
            raise Invalid_User_Type("Must be authenticated or guest user")
        attendee = self.get_attendee(user, event)
        if not attendee:
            raise Attendee_Does_Not_Exist("Attendee does not exist")
        attendee.delete()

    


    