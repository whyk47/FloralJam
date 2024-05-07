from django.core.mail import send_mail
from django.template.loader import get_template

from floral_jamming.models import EmailConfirmationToken, User

def send_verification_email(user: User, token: EmailConfirmationToken) -> None:
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