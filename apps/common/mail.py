from itertools import count

from django.conf import settings
from django.core import mail


class EmailMessage(mail.EmailMessage):
    """Email message with tag support."""

    def __init__(self, tag=None, **kwargs):
        super().__init__(**kwargs)
        self.tag = tag

    def get_connection(self, fail_silently=False):
        from django.core.mail import get_connection

        connection = self.connection
        if connection:
            return connection

        if self.tag:
            for x in count(1):
                tags = getattr(settings, f"M{x}_EMAIL_TAGS", None)

                if not tags:
                    break

                backend = getattr(settings, f"M{x}_EMAIL_BACKEND", "")
                host = getattr(settings, f"M{x}_EMAIL_HOST", "")
                port = getattr(settings, f"M{x}_EMAIL_PORT", "")
                use_tls = getattr(settings, f"M{x}_EMAIL_USE_TLS", True)
                username = getattr(settings, f"M{x}_EMAIL_HOST_USER", "")
                password = getattr(settings, f"M{x}_EMAIL_HOST_PASSWORD", "")
                from_email = getattr(settings, f"M{x}_DEFAULT_FROM_EMAIL", "")

                if self.tag in tags:
                    try:
                        connection = get_connection(
                            backend=backend,
                            fail_silently=fail_silently,
                            host=host,
                            port=port,
                            use_tls=use_tls,
                            username=username,
                            password=password,
                        )
                        self.from_email = from_email or self.from_email
                        break
                    except Exception:
                        pass

        if connection:
            return connection
        return super().get_connection(fail_silently=fail_silently)
