from django.template import Library

from ..util import is_authenticated_user

register = Library()

is_authenticated_user = register.filter(is_authenticated_user)
