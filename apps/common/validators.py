from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext_lazy as _


@deconstructible
class FileSizeValidator:
    """File size validator"""

    message = _("Maximum file size allowed is %(size)s %(unit)s.")
    code = "max_file_size"

    def __init__(self, max_size, message=None, code=None):
        self.max_size = max_size  # Max. size in KB.

        if message:
            self.message = message
        if code:
            self.code = code

    def __call__(self, value):
        file_size = value.size / 1024  # Convert Bytes to KB.

        if file_size > self.max_size:
            size, unit = self._get_size_and_unit(self.max_size)
            raise ValidationError(
                self.message,
                code=self.code,
                params={
                    "size": size,
                    "unit": unit,
                },
            )

    def __eq__(self, other):
        return (
            isinstance(other, self.__class__)
            and self.message == other.message
            and self.code == other.code
        )

    def _get_size_and_unit(self, size):
        if 1024 <= size < 1024**2:
            return round(size / 1024, 2), "MB"
        elif 1024**2 <= size < 1024**3:
            return round(size / 1024**2, 2), "GB"
        return size, "KB"
