from django.core.mail import send_mail
from django.template.loader import get_template
from django.urls import reverse
import os

from ...models import Attendee, EmailConfirmationToken, User

from ..email_service.email_service_exceptions import *

class Email_Service:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Email_Service, cls).__new__(cls)
        return cls.instance
        
    def get_token_by_id(self, token_id: str) -> EmailConfirmationToken:
        try:
            return EmailConfirmationToken.objects.get(id=token_id)
        except EmailConfirmationToken.DoesNotExist:
            raise Invalid_Token("This token is no longer valid")
        
    def __new_token(self, user: User) -> EmailConfirmationToken:
        return EmailConfirmationToken.objects.create(user=user)

    def delete_tokens(self, user: User) -> None:
        user.email_tokens.all().delete()

    def __send_email(self, user: User, subject: str, html_message: str) -> None:
        send_mail(
            subject=subject,
            message='',
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
            html_message=html_message
        )
        
    def __render_email_template(self, template: str, context: dict) -> str:
        email_template = get_template(f'floral_jamming/emails/{template}.html')
        return email_template.render(context=context)
    
    def send_verification_email(self, user: User, page: str, host: str) -> None:
        if user.num_valid_tokens() > 2:
            raise Too_Many_Attempts("You have exceeded the maximum number of email requests. Please try again later.")
        token = self.__new_token(user)
        url = host + reverse(f'floral_jamming:{page}', args=[user.id, token.id])
        message = self.__render_email_template('verification_email', {
            'url': url,
            'user': user
            })
        self.__send_email(
            user=user,
            subject=f'Floral Jamming - {"Reset Password" if user.is_email_verified else "Verify Email"}',
            html_message=message,
        )
    
    def verify_email_token(self, user: User, token: EmailConfirmationToken) -> None:
        if token.is_expired():
            token.delete()
            raise Invalid_Token("The token has expired")
        if user != token.user:
            raise Invalid_Token("The token does not belong to the requested user")
        
    def send_confirmation_email(self, attendee: Attendee, host: str) -> None:
        url = host + reverse("floral_jamming:details", args=[attendee.event.id])
        message = self.__render_email_template('confirmation_email', {
            'url': url,
            'attendee': attendee,
            }) 
        self.__send_email(
            user=attendee.user,
            subject='Floral Jamming - Event Confirmation',
            html_message=message,
            )
