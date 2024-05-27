import os
import sys

from celery.schedules import crontab
from kombu import Exchange, Queue

from conf import props

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = props.SECRET_KEY
SECRET_KEY_FALLBACKS = props.SECRET_KEY_FALLBACKS

DEBUG = props.DEBUG

ALLOWED_HOSTS = props.ALLOWED_HOSTS

ROOT_URLCONF = "conf.urls"

WSGI_APPLICATION = "conf.wsgi.application"

LANGUAGE_CODE = props.LANGUAGE_CODE
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)
TIME_ZONE = props.TIME_ZONE
USE_I18N = True
USE_L10N = True
USE_TZ = True

USE_STATIC = props.USE_STATIC
STATICFILES_DIRS = (os.path.join(BASE_DIR, "static"),)
STATIC_URL = os.path.join(props.STATIC_HOST, "static/")
STATIC_ROOT = os.path.join(BASE_DIR, "collectstatic")

USE_MEDIA = props.USE_MEDIA
MEDIA_URL = os.path.join(props.MEDIA_HOST, "media/")
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

# Django storages: Support for many storage backends in Django.

STORAGE_BACKENDS = {
    "staticfiles": "django.contrib.staticfiles.storage.StaticFilesStorage",
    "filesystem": "django.core.files.storage.FileSystemStorage",
    "dropbox": "storages.backends.dropbox.DropBoxStorage",
    "aws": "storages.backends.s3boto3.S3Boto3Storage",
    "gcloud": "storages.backends.gcloud.GoogleCloudStorage",
}

DROPBOX_OAUTH2_TOKEN = props.DROPBOX_OAUTH2_TOKEN
DROPBOX_ROOT_PATH = props.DROPBOX_ROOT_PATH

AWS_ACCESS_KEY_ID = props.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = props.AWS_SECRET_ACCESS_KEY
AWS_STORAGE_BUCKET_NAME = props.AWS_STORAGE_BUCKET_NAME
AWS_LOCATION = props.AWS_LOCATION

GS_FILE_OVERWRITE = False
GS_BUCKET_NAME = props.GS_BUCKET_NAME
GS_LOCATION = props.GS_LOCATION
GS_DEFAULT_ACL = props.GS_DEFAULT_ACL

STATICFILES_STORAGE = STORAGE_BACKENDS.get(props.STATICFILES_STORAGE_BACKEND)
DEFAULT_FILE_STORAGE = STORAGE_BACKENDS.get(props.MEDIA_STORAGE_BACKEND)

DATA_UPLOAD_MAX_MEMORY_SIZE = props.DATA_UPLOAD_MAX_MEMORY_SIZE
FILE_UPLOAD_MAX_MEMORY_SIZE = props.FILE_UPLOAD_MAX_MEMORY_SIZE

SESSION_ENGINES = {
    "db": "django.contrib.sessions.backends.db",
    "cache": "django.contrib.sessions.backends.cache",
    "cached_db": "django.contrib.sessions.backends.cached_db",
}

SESSION_ENGINE = SESSION_ENGINES.get(props.SESSION_ENGINE)

EMAIL_BACKENDS = {
    "smtp": "django.core.mail.backends.smtp.EmailBackend",
    "console": "django.core.mail.backends.console.EmailBackend",
    "filebased": "django.core.mail.backends.filebased.EmailBackend",
    "locmem": "django.core.mail.backends.locmem.EmailBackend",
    "dummy": "django.core.mail.backends.dummy.EmailBackend",
}

EMAIL_BACKEND = EMAIL_BACKENDS.get(props.EMAIL_BACKEND)
EMAIL_HOST = props.EMAIL_HOST
EMAIL_PORT = props.EMAIL_PORT
EMAIL_USE_TLS = props.EMAIL_USE_TLS
EMAIL_HOST_USER = props.EMAIL_HOST_USER
EMAIL_HOST_PASSWORD = props.EMAIL_HOST_PASSWORD
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "outbox")
DEFAULT_FROM_EMAIL = props.DEFAULT_FROM_EMAIL

props.set_mail_props(sys.modules[__name__], backends=EMAIL_BACKENDS)

CORS_ORIGIN_ALLOW_ALL = props.CORS_ALLOW_ALL
CORS_ORIGIN_WHITELIST = props.CORS_WHITELIST
CORS_ALLOW_METHODS = (
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
)
CORS_ALLOW_HEADERS = (
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
) + props.CORS_ALLOW_HEADERS
CORS_EXPOSE_HEADERS = props.CORS_EXPOSE_HEADERS

# Django channels framework: Project that takes Django
# and extends its abilities beyond HTTP - to handle WebSockets,
# chat protocols, IoT protocols, and more.


def _get_channels_layers_url(name, conf):
    urls = {
        "redis": "%(protocol)s://%(host)s:%(port)s/%(name)s",
        "redis+password": "%(protocol)s://%(user)s@%(host)s:%(port)s/%(name)s",
    }
    return (
        urls.get("redis+password" if name == "redis" and conf.get("user") else name)
        % conf
    )


USE_CHANNELS = props.USE_CHANNELS

ASGI_APPLICATION = "apis.ws.application"

CHANNELS_LAYERS_BACKENDS = {
    "locmem": {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer",
        },
    },
    "redis": {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [
                    _get_channels_layers_url(
                        "redis",
                        {
                            "protocol": props.CHANNELS_LAYERS_PROTOCOL or "redis",
                            "host": props.CHANNELS_LAYERS_HOST or "localhost",
                            "port": props.CHANNELS_LAYERS_PORT or "6379",
                            "name": props.CHANNELS_LAYERS_NAME or "0",
                            "user": props.CHANNELS_LAYERS_USER or "",
                            "password": props.CHANNELS_LAYERS_PASSWORD or "",
                        },
                    ),
                ],
                # "symmetric_encryption_keys": [SECRET_KEY],
            },
        },
    },
}

CHANNEL_LAYERS = CHANNELS_LAYERS_BACKENDS.get(props.CHANNELS_LAYERS_BACKEND)


def _get_caches_url(name, conf):
    urls = {
        "memcached": "%(host)s:%(port)s",
        "redis": "%(protocol)s://%(host)s:%(port)s/%(name)s",
        "redis+password": (
            "%(protocol)s://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s"
        ),
        "rediscache": "%(protocol)s://%(host)s:%(port)s/%(name)s",
        "rediscache+password": "%(protocol)s://%(user)s@%(host)s:%(port)s/%(name)s",
    }

    if name == "redis" and conf.get("user"):
        url = urls.get("redis+password")
    elif name == "rediscache" and conf.get("user"):
        url = urls.get("rediscache+password")
    else:
        url = urls.get(name)
    return url % conf


CACHES_BACKENDS = {
    "dummy": {
        "default": {
            "BACKEND": "django.core.cache.backends.dummy.DummyCache",
        },
    },
    "locmem": {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": props.CACHES_NAME or "cache",
        },
    },
    "memcached": {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": _get_caches_url(
                "memcached",
                {
                    "host": props.CACHES_HOST or "localhost",
                    "port": props.CACHES_PORT or "11211",
                },
            ),
        },
    },
    "redis": {
        "default": {
            "BACKEND": "django.core.cache.backends.redis.RedisCache",
            "LOCATION": _get_caches_url(
                "redis",
                {
                    "protocol": props.CACHES_PROTOCOL or "redis",
                    "host": props.CACHES_HOST or "localhost",
                    "port": props.CACHES_PORT or "6379",
                    "name": props.CACHES_NAME or "0",
                    "user": props.CACHES_USER or "",
                    "password": props.CACHES_PASSWORD or "",
                },
            ),
        },
    },
    "db": {
        "default": {
            "BACKEND": "django.core.cache.backends.db.DatabaseCache",
            "LOCATION": f"cache_{props.CACHES_NAME or 'cache'}",
        },
    },
    "rediscache": {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": _get_caches_url(
                "rediscache",
                {
                    "protocol": props.CACHES_PROTOCOL or "redis",
                    "host": props.CACHES_HOST or "localhost",
                    "port": props.CACHES_PORT or "6379",
                    "name": props.CACHES_NAME or "0",
                    "user": props.CACHES_USER or "",
                },
            ),
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "PASSWORD": props.CACHES_PASSWORD or "",
            },
        },
    },
}

CACHES = CACHES_BACKENDS.get(props.CACHES_BACKEND)

DB_BACKENDS = {
    "sqlite3": {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
            "CONN_MAX_AGE": props.DB_CONN_MAX_AGE,
        },
    },
    "postgresql": {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": props.DB_NAME or "db",
            "USER": props.DB_USER or "postgres",
            "PASSWORD": props.DB_PASSWORD or "postgres",
            "HOST": props.DB_HOST or "localhost",
            "PORT": props.DB_PORT or "5432",
            "CONN_MAX_AGE": props.DB_CONN_MAX_AGE,
            "DISABLE_SERVER_SIDE_CURSORS": True,
            "OPTIONS": {
                "sslmode": "required" if props.DB_SSL else None,
            },
            "TEST": {
                "NAME": f"test_{props.DB_NAME or 'db'}",
                "CHARSET": "UTF8",
            },
        },
    },
    "mysql": {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "NAME": props.DB_NAME or "db",
            "USER": props.DB_USER or "root",
            "PASSWORD": props.DB_PASSWORD or "root",
            "HOST": props.DB_HOST or "localhost",
            "PORT": props.DB_PORT or "3306",
            "CONN_MAX_AGE": props.DB_CONN_MAX_AGE,
            "OPTIONS": {
                "init_command": "SET sql_mode='STRICT_TRANS_TABLES'",
            },
            "TEST": {
                "NAME": f"test_{props.DB_NAME or 'db'}",
                "CHARSET": "utf8",
                "COLLATION": "utf8_general_ci",
            },
        }
    },
    "cockroachdb": {
        "default": {
            "ENGINE": "django_cockroachdb",
            "NAME": props.DB_NAME or "db",
            "USER": props.DB_USER or "root",
            "PASSWORD": props.DB_PASSWORD or "root",
            "HOST": props.DB_HOST or "localhost",
            "PORT": props.DB_PORT or "26257",
            "CONN_MAX_AGE": props.DB_CONN_MAX_AGE,
            "OPTIONS": {
                "sslmode": "required" if props.DB_SSL else None,
            },
            "TEST": {
                "NAME": f"test_{props.DB_NAME or 'db'}",
                "CHARSET": "UTF8",
            },
        },
    },
}

DATABASES = DB_BACKENDS.get(props.DB_BACKEND)

SQL_DEBUG = props.SQL_DEBUG

USE_GRAPHQL = props.USE_GRAPHQL

GRAPHENE = {
    "SCHEMA": "apis.gql.schema",
    "RELAY_CONNECTION_MAX_LIMIT": props.GQL_CONNECTION_LIMIT,
    "RELAY_CONNECTION_ENFORCE_FIRST_OR_LAST": True,
    "GRAPHIQL_HEADER_EDITOR_ENABLED": True,
    "GRAPHIQL_SHOULD_PERSIST_HEADERS": True,
    "GQL_MAX_SIZE": props.GQL_MAX_SIZE,
    "GQL_MAX_DEFINITIONS": props.GQL_MAX_DEFINITIONS,
    "GQL_MAX_DEPTH": props.GQL_MAX_DEPTH,
    "GQL_MAX_FIELDS": props.GQL_MAX_FIELDS,
    "GQL_INTROSPECTION": props.GQL_INTROSPECTION,
}

GRAPHIQL = props.GQL_GRAPHIQL

# Celery: Distributed task queue. Celery is an
# asynchronous task queue/job queue based on distributed message passing.


def _get_celery_broker_url(name, conf):
    urls = {
        "sqlite3": "%(protocol)s://%(name)s",
        "postgresql": "%(protocol)s://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s",
        "mysql": "%(protocol)s://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s",
        "rabbitmq": "%(protocol)s://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s",
        "redis": "%(protocol)s://%(host)s:%(port)s/%(name)s",
        "redis+password": "%(protocol)s://%(password)s@%(host)s:%(port)s/%(name)s",
    }
    return (
        urls.get("redis+password" if name == "redis" and conf.get("password") else name)
        % conf
    )


CELERY_BROKER_BACKENDS = {
    "sqlite3": _get_celery_broker_url(
        "sqlite3",
        {
            "protocol": "sqla+sqlite",
            "name": "/celery.sqlite3",
        },
    ),
    "postgresql": _get_celery_broker_url(
        "postgresql",
        {
            "protocol": "sqla+postgresql",
            "host": props.CELERY_BROKER_HOST or "localhost",
            "port": props.CELERY_BROKER_PORT or "5432",
            "name": props.CELERY_BROKER_NAME or "db",
            "user": props.CELERY_BROKER_USER or "postgres",
            "password": props.CELERY_BROKER_PASSWORD or "postgres",
        },
    ),
    "mysql": _get_celery_broker_url(
        "mysql",
        {
            "protocol": "sqla+mysql",
            "host": props.CELERY_BROKER_HOST or "localhost",
            "port": props.CELERY_BROKER_PORT or "3306",
            "name": props.CELERY_BROKER_NAME or "db",
            "user": props.CELERY_BROKER_USER or "root",
            "password": props.CELERY_BROKER_PASSWORD or "root",
        },
    ),
    "rabbitmq": _get_celery_broker_url(
        "rabbitmq",
        {
            "protocol": props.CELERY_BROKER_PROTOCOL or "amqp",
            "host": props.CELERY_BROKER_HOST or "localhost",
            "port": props.CELERY_BROKER_PORT or "5672",
            "name": props.CELERY_BROKER_NAME or "app",
            "user": props.CELERY_BROKER_USER or "admin",
            "password": props.CELERY_BROKER_PASSWORD or "admin",
        },
    ),
    "redis": _get_celery_broker_url(
        "redis",
        {
            "protocol": props.CELERY_BROKER_PROTOCOL or "redis",
            "host": props.CELERY_BROKER_HOST or "localhost",
            "port": props.CELERY_BROKER_PORT or "6379",
            "name": props.CELERY_BROKER_NAME or "0",
            "user": props.CELERY_BROKER_USER or "",
            "password": props.CELERY_BROKER_PASSWORD or "",
        },
    ),
}

CELERY_BROKER_URL = CELERY_BROKER_BACKENDS.get(props.CELERY_BROKER_BACKEND)

CELERY_BEAT_SCHEDULE = {
    "run-every-minute": {
        "task": "app.common.math.add",
        "schedule": crontab(),
        "args": (
            2,
            5,
        ),
    },
}

CELERY_TASK_QUEUES = (
    Queue(
        "app.default",
        Exchange("app.default", type="topic"),
        routing_key="app.default.#",
    ),
    Queue(
        "app.mail.outbox",
        Exchange("app.mail", type="topic"),
        routing_key="app.mail.outbox.#",
    ),
    Queue(
        "app.math.calculator",
        Exchange("app.math", type="topic"),
        routing_key="app.math.calculator.#",
    ),
)

CELERY_TASK_ROUTES = (
    [
        (
            "app.accounts.mail.*",
            {
                "queue": "app.mail.outbox",
                "exchange": "app.mail",
                "exchange_type": "topic",
                "routing_key": "app.mail.outbox.accounts",
            },
        ),
        (
            "app.common.mail.*",
            {
                "queue": "app.mail.outbox",
                "exchange": "app.mail",
                "exchange_type": "topic",
                "routing_key": "app.mail.outbox.common",
            },
        ),
        (
            "app.common.math.*",
            {
                "queue": "app.math.calculator",
                "exchange": "app.math",
                "exchange_type": "topic",
                "routing_key": "app.math.calculator.common",
            },
        ),
    ],
)

# Sentry: Error tracking that helps
# developers monitor and fix crashes in real time.

USE_SENTRY = props.USE_SENTRY
SENTRY_DSN = props.SENTRY_DSN
SENTRY_DEBUG = props.SENTRY_DEBUG
SENTRY_RELEASE = props.SENTRY_RELEASE
SENTRY_ENVIRONMENT = props.SENTRY_ENVIRONMENT
SENTRY_SERVER_NAME = props.SENTRY_SERVER_NAME

# Admin site

USE_ADMIN_SITE = props.USE_ADMIN_SITE

# REST framework

USE_DRF = props.USE_DRF
DRF_SWAGGER = props.DRF_SWAGGER

# Extra

AUTH_TOKEN_TYPE = props.AUTH_TOKEN_TYPE
AUTH_TOKEN_AGE = props.AUTH_TOKEN_AGE
AUTH_REFRESH_TOKEN_TYPE = props.AUTH_REFRESH_TOKEN_TYPE
AUTH_REFRESH_TOKEN_AGE = props.AUTH_REFRESH_TOKEN_AGE
SIGNUP_TOKEN_TYPE = props.SIGNUP_TOKEN_TYPE
SIGNUP_TOKEN_AGE = props.SIGNUP_TOKEN_AGE
SIGNUP_URL = props.SIGNUP_URL
PASSWD_TOKEN_TYPE = props.PASSWD_TOKEN_TYPE
PASSWD_TOKEN_AGE = props.PASSWD_TOKEN_AGE
PASSWD_URL = props.PASSWD_URL

USE_DUMMY = props.USE_DUMMY

# CSRF

CSRF_TRUSTED_ORIGINS = props.CSRF_TRUSTED_ORIGINS
