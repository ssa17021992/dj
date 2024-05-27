import os

os.environ["USE_DRF"] = "True"
os.environ["USE_GRAPHQL"] = "True"
os.environ["USE_DUMMY"] = "True"
os.environ["CACHES_BACKEND"] = "dummy"

from conf.settings import *  # noqa

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
