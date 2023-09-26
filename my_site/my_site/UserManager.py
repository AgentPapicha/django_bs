from django.contrib.auth.models import User, BaseUserManager
from django.core.mail import send_mail

from settings import DEFAULT_FROM_EMAIL


class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None, *args, **kwargs):
        response = super().create_user(username, email, password=None, *args, **kwargs)
        send_mail(subject="Account active",
                  message="Your account is active",
                  from_email=DEFAULT_FROM_EMAIL,
                  recipient_list=[email]
                  )

        return response


class CustomUser(User):
    objects = UserManager()

