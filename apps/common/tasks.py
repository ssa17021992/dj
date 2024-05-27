from celery import shared_task

from apps.common.decorators import task_lock, task_throttle
from apps.common.mail import EmailMessage


@shared_task(name="app.common.echo")
@task_throttle(name="common.echo", limit=10, timeout=600)
def echo(message):
    """Echo"""
    return message


@shared_task(name="app.common.math.add")
def add(a, b):
    """Add"""
    return a + b


@shared_task(name="app.common.mail.send_mail")
@task_lock(name="common.send_mail")
def send_mail(subject, body, to):
    """Send mail"""
    message = EmailMessage(tag="common", subject=subject, body=body, to=[to])
    return message.send(fail_silently=True)
