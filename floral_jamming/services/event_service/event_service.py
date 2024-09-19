from datetime import datetime
from typing import *
from django.db.models.query import QuerySet

from .event_service_exceptions import *
from ..auth_service.auth_service import Auth_Service
from ...models import User, Event, Attendee
from ...forms import AttendeeForm, EventForm, GuestForm
from ...util import get_data, Invalid_Form


class Event_Service:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Event_Service, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        self._auth_service = Auth_Service()

    @property
    def __auth_service(self):
        return self._auth_service

    def create_event(self, user: User, form: EventForm) -> Event:
        auth_service = self.__auth_service
        if not auth_service.is_staff_user(user):
            raise Invalid_User_Type("Must be staff user to create event")
        data = get_data(form)
        event = form.save(commit=False)
        event.creator = user
        event.save()
        return event
        
    def __validate_event_capacity(self, event: Event, capacity: int) -> None:
        if event.num_attendees() > capacity:
            raise Invalid_Form("Number of attendees registered exceeds capacity of event")

    def update_event(self, event_id: int, user: User, form: EventForm) -> Event:
        event = self.get_event_by_id(event_id)
        if not event:
            raise Event_Does_Not_Exist("Event does not exist")
        auth_service = self.__auth_service
        if not auth_service.is_staff_user(user):
            raise Invalid_User_Type("Must be staff user to create event")
        if not user == event.creator:
            raise Invalid_User_Type("User must be event creator to update event")
        data = get_data(form)
        self.__validate_event_capacity(event, data['capacity'])
        event, created = user.events.update_or_create(id=event_id, defaults=data)
        return event
        
    def get_events(self, user: User) -> Optional[QuerySet]:
        auth_service = self.__auth_service
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
        auth_service = self.__auth_service
        if auth_service.is_anonymous_user(user):
            return None
        return event.attendees.filter(user=user).first()
    
    @staticmethod
    def get_pax(user: User, event: Event) -> int:
        if user.is_anonymous:
            return 0
        return event.attendees.filter(user=user).first().pax
    
    def get_user_attendees(self, user: User) -> QuerySet:
        return user.attendees.all()
    
    def __validate_pax(self, user: User, event: Event, pax: int) -> None:
        attendee = self.get_attendee(user, event)
        attendee_pax = attendee.pax if attendee else 0
        if pax > event.remaining_slots() + attendee_pax:
            raise Invalid_Form("Number of pax exceeds capacity of event")
    
    def __validate_guest_forms(self, guest: User, event: Event, attendee_data: dict, guest_data: dict) -> None:
        self.__validate_pax(guest, event, attendee_data['pax'])        
        
        user_attendee = event.attendees.filter(user__email=guest_data['email']).first()
        if (user_attendee and user_attendee.user != guest) or guest_data['email'] == event.creator.email:
            raise Invalid_Form("Email already in use")
    
    def create_or_update_user_attendee(self, user: User, event: Event, attendee_form: AttendeeForm) -> Attendee:
        if not self.__auth_service.is_authenticated_user(user):
            raise Invalid_User_Type("Must be authenticated user")
        data = get_data(attendee_form)
        pax = data['pax']
        self.__validate_pax(user, event, pax)
        attendee, created = event.attendees.update_or_create(
            user=user, 
            defaults={
                'pax': pax,
                'is_email_verified': True,
            })
        return attendee
    
    def create_or_update_guest_attendee(self, user: User, event: Event, attendee_form: AttendeeForm, guest_form: GuestForm) -> Attendee:
        if not self.__auth_service.is_guest_user(user):
            raise Invalid_User_Type("Must be guest user")
        attendee_data, guest_data = get_data(attendee_form), get_data(guest_form)
        self.__validate_guest_forms(user, event, attendee_data, guest_data)
        self.__auth_service.update_user_details(guest_data, user)
        attendee, created = event.attendees.update_or_create(
            user=user, 
            defaults={
                **attendee_data,
                'is_email_verified': self.__auth_service.is_email_verified(user),
                })
        return attendee
    
    def delete_attendee(self, user: User, event: Event) -> None:
        auth_service = self.__auth_service
        if auth_service.is_anonymous_user(user):
            raise Invalid_User_Type("Must be authenticated or guest user")
        attendee = self.get_attendee(user, event)
        if not attendee:
            raise Attendee_Does_Not_Exist("Attendee does not exist")
        attendee.delete()

    def set_email_verified(self, user: User) -> QuerySet:
        self.__auth_service.set_email_verified(user)
        attendees = self.get_user_attendees(user).filter(is_email_verified=False)
        for attendee in attendees:
            attendee.is_email_verified = True
            attendee.save()
        return attendees
        
    


    