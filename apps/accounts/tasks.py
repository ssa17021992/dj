import os

from celery import shared_task
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

from apps.common.decorators import task_lock
from apps.common.mail import EmailMessage


@shared_task(name="app.accounts.mail.send_signup_mail")
@task_lock(name="accounts.send_signup_mail", attr=lambda code, email: email)
def send_signup_mail(code, email):
    """Send signup mail"""
    html = render_to_string(
        "mail/accounts/signup_code.html",
        {
            "code": code,
        },
    )

    message = EmailMessage(
        tag="accounts", subject=_("Signup code"), body=html, to=[email]
    )
    message.content_subtype = "html"
    return message.send(fail_silently=True)


@shared_task(name="app.accounts.mail.send_passwd_reset_mail")
@task_lock(
    name="accounts.send_passwd_reset_mail", attr=lambda token, username, email: username
)
def send_passwd_reset_mail(token, username, email):
    """Send passwd reset mail"""
    html = render_to_string(
        "mail/accounts/passwd_reset.html",
        {
            "username": username,
            "url": os.path.join(settings.PASSWD_URL, token),
        },
    )

    message = EmailMessage(
        tag="accounts", subject=_("Password reset"), body=html, to=[email]
    )
    message.content_subtype = "html"
    return message.send(fail_silently=True)
