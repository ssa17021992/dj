from django.utils.module_loading import import_string


def get_auth_backend(name):
    """Get auth backend."""
    backend = import_string("apps.accounts.auth.backends.%s" % name)
    return backend.AuthBackend()
