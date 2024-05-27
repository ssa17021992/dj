from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.common.defaults import b64_id


class Model(models.Model):
    """Model"""

    id = models.CharField(
        max_length=22,
        default=b64_id,
        editable=False,
        primary_key=True,
        verbose_name=_("ID"),
    )

    def __str__(self):
        return str(self.pk or "")

    class Meta:
        abstract = True
