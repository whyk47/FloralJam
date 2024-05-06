from django.template import Library

from ..services.auth_service.auth_service import Auth_Service


register = Library()

is_authenticated_user = register.filter(Auth_Service.is_authenticated_user)
is_guest_user = register.filter(Auth_Service.is_guest_user)
is_anonymous_user = register.filter(Auth_Service.is_anonymous_user)
is_staff_user = register.filter(Auth_Service.is_staff_user)
