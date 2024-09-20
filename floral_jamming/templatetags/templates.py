from django.template import Library

from ..services.auth_service.auth_service import Auth_Service
from ..services.event_service.event_service import Event_Service
from ..util import multiply


register = Library()

is_authenticated_user = register.filter(Auth_Service.is_authenticated_user)
is_guest_user = register.filter(Auth_Service.is_guest_user)
is_anonymous_user = register.filter(Auth_Service.is_anonymous_user)
is_staff_user = register.filter(Auth_Service.is_staff_user)
is_email_verified = register.filter(Auth_Service.is_email_verified)
get_pax = register.filter(Event_Service.get_pax)

@register.filter
def multiply(x: int, y: int) -> int:
    return x * y

@register.filter
def addstr(arg1, arg2):
    """concatenate arg1 & arg2"""
    return str(arg1) + str(arg2)
