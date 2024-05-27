from collections.abc import Sequence
from numbers import Integral

from django.core import checks

from apps.cors.conf import conf

try:
    from django.utils import six
except ImportError:
    import six


@checks.register
def check_settings(app_configs, **kwargs):
    errors = []

    if not is_sequence(conf.CORS_ALLOW_HEADERS, six.string_types):
        errors.append(
            checks.Error(
                "CORS_ALLOW_HEADERS should be a sequence of strings.", id="cors.E001"
            )
        )

    if not is_sequence(conf.CORS_ALLOW_METHODS, six.string_types):
        errors.append(
            checks.Error(
                "CORS_ALLOW_METHODS should be a sequence of strings.", id="cors.E002"
            )
        )

    if not isinstance(conf.CORS_ALLOW_CREDENTIALS, bool):
        errors.append(
            checks.Error("CORS_ALLOW_CREDENTIALS should be a bool.", id="cors.E003")
        )

    if (
        not isinstance(conf.CORS_PREFLIGHT_MAX_AGE, Integral)
        or conf.CORS_PREFLIGHT_MAX_AGE < 0
    ):
        errors.append(
            checks.Error(
                (
                    "CORS_PREFLIGHT_MAX_AGE should be an "
                    "integer greater than or equal to zero."
                ),
                id="cors.E004",
            )
        )

    if not isinstance(conf.CORS_ORIGIN_ALLOW_ALL, bool):
        errors.append(
            checks.Error("CORS_ORIGIN_ALLOW_ALL should be a bool.", id="cors.E005")
        )

    if not is_sequence(conf.CORS_ORIGIN_WHITELIST, six.string_types):
        errors.append(
            checks.Error(
                "CORS_ORIGIN_WHITELIST should be a sequence of strings.", id="cors.E006"
            )
        )

    if not is_sequence(conf.CORS_EXPOSE_HEADERS, six.string_types):
        errors.append(
            checks.Error("CORS_EXPOSE_HEADERS should be a sequence.", id="cors.E007")
        )

    return errors


def is_sequence(thing, types):
    return isinstance(thing, Sequence) and all(isinstance(x, types) for x in thing)
