from django.core.mail import send_mail
from django.template.loader import get_template

from floral_jamming.models import EmailConfirmationToken, User
from floral_jamming.services.email_service.email_service_exceptions import *

class Email_Service:
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(Email_Service, cls).__new__(cls)
        return cls.instance
        
    def get_token_by_id(self, token_id: str) -> EmailConfirmationToken:
        try:
            return EmailConfirmationToken.objects.get(id=token_id)
        except EmailConfirmationToken.DoesNotExist:
            raise Invalid_Token("The token does not exist")
        
    def __new_token(self, user: User) -> EmailConfirmationToken:
        return EmailConfirmationToken.objects.create(user=user)

    def __delete_tokens(self, user: User) -> None:
        user.email_tokens.all().delete()
        
    def send_verification_email(self, user: User) -> None:
        if user.num_valid_tokens() > 2:
            raise Too_Many_Attempts("You have exceeded the maximum number of attempts. Please try again later.")
        token = self.__new_token(user)
        data = {
            'user_id': str(user.id),
            'token_id': str(token.id),
        }
        message = get_template('floral_jamming/verification_email.hmtl').render(data)
        send_mail(
            subject='Floral Jamming - Verify Email',
            message=message,
            from_email=None,
            recipient_list=[user.email],
            fail_silently=False,
        )
    
    def verify_email_token(self, user: User, token: EmailConfirmationToken) -> None:
        if token.is_expired():
            token.delete()
            raise Invalid_Token("The token has expired")
        if user != token.user:
            raise Invalid_Token("The token does not belong to the requested user")
        self.__delete_tokens(user)