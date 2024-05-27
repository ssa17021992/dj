import os
from itertools import count

__all__ = (
    "to_bool",
    "to_int",
    "to_float",
    "to_str",
    "to_none",
    "to_list",
    "to_tuple",
    "props",
)


def to_bool(value):
    return value.lower() == "true"


def to_int(value):
    try:
        value = int(value)
    except ValueError:
        return 0
    return value


def to_float(value):
    try:
        value = float(value)
    except ValueError:
        return 0.0
    return value


def to_str(value):
    return str(value).strip()


def to_none(value):
    return None if value.lower() == "none" else value


def to_list(value):
    return [s.strip() for s in value.split(",") if s.strip()]


def to_tuple(value):
    return tuple(to_list(value))


class Props:
    """Configuration properties."""

    def __init__(self):
        self.set_mail_props()

    def set_mail_props(self, obj=None, backends=None):
        props = os.environ
        obj = obj or self
        backends = backends or {}

        for x in count(1):
            prop_tags = f"M{x}_EMAIL_TAGS"
            tags = props.get(prop_tags)

            if not tags:
                break

            prop_backend = f"M{x}_EMAIL_BACKEND"
            prop_host = f"M{x}_EMAIL_HOST"
            prop_port = f"M{x}_EMAIL_PORT"
            prop_use_tls = f"M{x}_EMAIL_USE_TLS"
            prop_host_user = f"M{x}_EMAIL_HOST_USER"
            prop_host_password = f"M{x}_EMAIL_HOST_PASSWORD"
            prop_default_from_email = f"M{x}_DEFAULT_FROM_EMAIL"

            backend = props.get(prop_backend, "filebased")
            host = props.get(prop_host, "smtp.gmail.com")
            port = props.get(prop_port, "587")
            use_tls = props.get(prop_use_tls, "True")
            host_user = props.get(prop_host_user, "app@mail.com")
            host_password = props.get(prop_host_password, "")
            default_from_email = props.get(prop_default_from_email, host_user)

            setattr(obj, prop_tags, to_tuple(tags))
            setattr(obj, prop_backend, backends.get(backend, backend))
            setattr(obj, prop_host, host)
            setattr(obj, prop_port, port)
            setattr(obj, prop_use_tls, to_bool(use_tls))
            setattr(obj, prop_host_user, host_user)
            setattr(obj, prop_host_password, host_password)
            setattr(obj, prop_default_from_email, default_from_email)

    @property
    def SECRET_KEY(self):
        return to_str(
            os.environ.get(
                "SECRET_KEY", ")&!pn-u*ijid#&*nzcvse!w^b1#o3ix)cilvq+838yov$q5o1i"
            )
        )

    @property
    def SECRET_KEY_FALLBACKS(self):
        return to_tuple(os.environ.get("SECRET_KEY_FALLBACKS", ""))

    @property
    def DEBUG(self):
        return to_bool(os.environ.get("DEBUG", "True"))

    @property
    def ALLOWED_HOSTS(self):
        return to_tuple(os.environ.get("ALLOWED_HOSTS", "*"))

    @property
    def CORS_ALLOW_ALL(self):
        return to_bool(os.environ.get("CORS_ALLOW_ALL", "True"))

    @property
    def CORS_WHITELIST(self):
        return to_tuple(
            os.environ.get(
                "CORS_WHITELIST",
                r"^(https?://)?localhost:3000$, ^(https?://)?(\w+\.)?example\.com$",
            )
        )

    @property
    def CORS_ALLOW_HEADERS(self):
        return to_tuple(
            os.environ.get("CORS_ALLOW_HEADERS", "x-request-id, x-time-zone")
        )

    @property
    def CORS_EXPOSE_HEADERS(self):
        return to_tuple(os.environ.get("CORS_EXPOSE_HEADERS", "*"))

    @property
    def LANGUAGE_CODE(self):
        return to_str(os.environ.get("LANGUAGE_CODE", "en-us"))

    @property
    def TIME_ZONE(self):
        return to_str(os.environ.get("TIME_ZONE", "UTC"))

    @property
    def DROPBOX_OAUTH2_TOKEN(self):
        return to_str(
            os.environ.get(
                "DROPBOX_OAUTH2_TOKEN",
                "lSTaTa0KhvAAAAAAAAAACYx0VRVjKNaJTSa5ryIiit92eZS_GvY2rTzLwOOTFfyO",
            )
        )

    @property
    def DROPBOX_ROOT_PATH(self):
        return to_str(os.environ.get("DROPBOX_ROOT_PATH", "app"))

    @property
    def AWS_ACCESS_KEY_ID(self):
        return to_str(os.environ.get("AWS_ACCESS_KEY_ID", "ERIAIUDVFEKLS35MLTIP"))

    @property
    def AWS_SECRET_ACCESS_KEY(self):
        return to_str(
            os.environ.get(
                "AWS_SECRET_ACCESS_KEY", "20ME7ekjS/IksxDfDrGDCO/3jSzkFPo8EaSe2ZjR"
            )
        )

    @property
    def AWS_STORAGE_BUCKET_NAME(self):
        return to_str(os.environ.get("AWS_STORAGE_BUCKET_NAME", "app"))

    @property
    def AWS_LOCATION(self):
        return to_str(os.environ.get("AWS_LOCATION", "app"))

    @property
    def GOOGLE_APPLICATION_CREDENTIALS(self):
        return to_str(os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "gcloud.json"))

    @property
    def GS_BUCKET_NAME(self):
        return to_str(os.environ.get("GS_BUCKET_NAME", "app"))

    @property
    def GS_LOCATION(self):
        return to_str(os.environ.get("GS_LOCATION", "app"))

    @property
    def GS_DEFAULT_ACL(self):
        return to_none(os.environ.get("GS_DEFAULT_ACL", "None"))

    @property
    def USE_STATIC(self):
        return to_bool(os.environ.get("USE_STATIC", "True"))

    @property
    def STATICFILES_STORAGE_BACKEND(self):
        return to_str(os.environ.get("STATICFILES_STORAGE_BACKEND", "staticfiles"))

    @property
    def STATIC_HOST(self):
        return to_str(os.environ.get("STATIC_HOST", "/"))

    @property
    def USE_MEDIA(self):
        return to_bool(os.environ.get("USE_MEDIA", "True"))

    @property
    def MEDIA_STORAGE_BACKEND(self):
        return to_str(os.environ.get("MEDIA_STORAGE_BACKEND", "filesystem"))

    @property
    def MEDIA_HOST(self):
        return to_str(os.environ.get("MEDIA_HOST", "/"))

    @property
    def DATA_UPLOAD_MAX_MEMORY_SIZE(self):
        return to_int(os.environ.get("DATA_UPLOAD_MAX_MEMORY_SIZE", "2621440"))

    @property
    def FILE_UPLOAD_MAX_MEMORY_SIZE(self):
        return to_int(os.environ.get("FILE_UPLOAD_MAX_MEMORY_SIZE", "2621440"))

    @property
    def USE_CHANNELS(self):
        return to_bool(os.environ.get("USE_CHANNELS", "False"))

    @property
    def CHANNELS_LAYERS_BACKEND(self):
        return to_str(os.environ.get("CHANNELS_LAYERS_BACKEND", "locmem"))

    @property
    def CHANNELS_LAYERS_PROTOCOL(self):
        return to_str(os.environ.get("CHANNELS_LAYERS_PROTOCOL", ""))

    @property
    def CHANNELS_LAYERS_HOST(self):
        return to_str(os.environ.get("CHANNELS_LAYERS_HOST", "localhost"))

    @property
    def CHANNELS_LAYERS_PORT(self):
        return to_str(os.environ.get("CHANNELS_LAYERS_PORT", ""))

    @property
    def CHANNELS_LAYERS_NAME(self):
        return to_str(os.environ.get("CHANNELS_LAYERS_NAME", ""))

    @property
    def CHANNELS_LAYERS_USER(self):
        return to_str(os.environ.get("CHANNELS_LAYERS_USER", ""))

    @property
    def CHANNELS_LAYERS_PASSWORD(self):
        return to_str(os.environ.get("CHANNELS_LAYERS_PASSWORD", ""))

    @property
    def CACHES_BACKEND(self):
        return to_str(os.environ.get("CACHES_BACKEND", "locmem"))

    @property
    def CACHES_PROTOCOL(self):
        return to_str(os.environ.get("CACHES_PROTOCOL", ""))

    @property
    def CACHES_HOST(self):
        return to_str(os.environ.get("CACHES_HOST", "localhost"))

    @property
    def CACHES_PORT(self):
        return to_str(os.environ.get("CACHES_PORT", ""))

    @property
    def CACHES_NAME(self):
        return to_str(os.environ.get("CACHES_NAME", ""))

    @property
    def CACHES_USER(self):
        return to_str(os.environ.get("CACHES_USER", ""))

    @property
    def CACHES_PASSWORD(self):
        return to_str(os.environ.get("CACHES_PASSWORD", ""))

    @property
    def DB_BACKEND(self):
        return to_str(os.environ.get("DB_BACKEND", "sqlite3"))

    @property
    def DB_HOST(self):
        return to_str(os.environ.get("DB_HOST", "localhost"))

    @property
    def DB_PORT(self):
        return to_str(os.environ.get("DB_PORT", ""))

    @property
    def DB_SSL(self):
        return to_bool(os.environ.get("DB_SSL", "False"))

    @property
    def DB_CONN_MAX_AGE(self):
        value = os.environ.get("DB_CONN_MAX_AGE", "0")
        return None if to_none(value) is None else to_int(value)

    @property
    def DB_NAME(self):
        return to_str(os.environ.get("DB_NAME", "db"))

    @property
    def DB_USER(self):
        return to_str(os.environ.get("DB_USER", ""))

    @property
    def DB_PASSWORD(self):
        return to_str(os.environ.get("DB_PASSWORD", ""))

    @property
    def SQL_DEBUG(self):
        return to_bool(os.environ.get("SQL_DEBUG", "False"))

    @property
    def EMAIL_BACKEND(self):
        return to_str(os.environ.get("EMAIL_BACKEND", "filebased"))

    @property
    def EMAIL_HOST(self):
        return to_str(os.environ.get("EMAIL_HOST", "smtp.gmail.com"))

    @property
    def EMAIL_PORT(self):
        return to_int(os.environ.get("EMAIL_PORT", "587"))

    @property
    def EMAIL_USE_TLS(self):
        return to_bool(os.environ.get("EMAIL_USE_TLS", "True"))

    @property
    def EMAIL_HOST_USER(self):
        return to_str(os.environ.get("EMAIL_HOST_USER", "app@mail.com"))

    @property
    def EMAIL_HOST_PASSWORD(self):
        return to_str(os.environ.get("EMAIL_HOST_PASSWORD", ""))

    @property
    def DEFAULT_FROM_EMAIL(self):
        return to_str(os.environ.get("DEFAULT_FROM_EMAIL", "app@mail.com"))

    @property
    def CELERY_BROKER_BACKEND(self):
        return to_str(os.environ.get("CELERY_BROKER_BACKEND", "sqlite3"))

    @property
    def CELERY_BROKER_PROTOCOL(self):
        return to_str(os.environ.get("CELERY_BROKER_PROTOCOL", ""))

    @property
    def CELERY_BROKER_HOST(self):
        return to_str(os.environ.get("CELERY_BROKER_HOST", "localhost"))

    @property
    def CELERY_BROKER_PORT(self):
        return to_str(os.environ.get("CELERY_BROKER_PORT", ""))

    @property
    def CELERY_BROKER_NAME(self):
        return to_str(os.environ.get("CELERY_BROKER_NAME", ""))

    @property
    def CELERY_BROKER_USER(self):
        return to_str(os.environ.get("CELERY_BROKER_USER", ""))

    @property
    def CELERY_BROKER_PASSWORD(self):
        return to_str(os.environ.get("CELERY_BROKER_PASSWORD", ""))

    @property
    def USE_SENTRY(self):
        return to_bool(os.environ.get("USE_SENTRY", "False"))

    @property
    def SENTRY_DSN(self):
        return to_str(
            os.environ.get(
                "SENTRY_DSN",
                "https://afb2183da948402b905928b5b522d62a:851e958dc5124530a2c41631a55c4c94@sentry.io/270851",  # noqa
            )
        )

    @property
    def SENTRY_DEBUG(self):
        return to_bool(os.environ.get("SENTRY_DEBUG", "False"))

    @property
    def SENTRY_RELEASE(self):
        return to_str(os.environ.get("SENTRY_RELEASE", "1.0"))

    @property
    def SENTRY_ENVIRONMENT(self):
        return to_str(os.environ.get("SENTRY_ENVIRONMENT", "development"))

    @property
    def SENTRY_SERVER_NAME(self):
        return to_str(os.environ.get("SENTRY_SERVER_NAME", "app"))

    @property
    def CSRF_TRUSTED_ORIGINS(self):
        return to_tuple(
            os.environ.get(
                "CSRF_TRUSTED_ORIGINS",
                "https://site.example.com, https://*.example.com",
            )
        )

    @property
    def AUTH_TOKEN_TYPE(self):
        return to_str(os.environ.get("AUTH_TOKEN_TYPE", "auth"))

    @property
    def AUTH_TOKEN_AGE(self):
        return to_int(os.environ.get("AUTH_TOKEN_AGE", "316224000"))  # noqa 10 years

    @property
    def AUTH_REFRESH_TOKEN_TYPE(self):
        return to_str(os.environ.get("AUTH_REFRESH_TOKEN_TYPE", "auth_refresh"))

    @property
    def AUTH_REFRESH_TOKEN_AGE(self):
        return to_int(
            os.environ.get("AUTH_REFRESH_TOKEN_AGE", "316224000")
        )  # noqa 10 years

    @property
    def SIGNUP_TOKEN_TYPE(self):
        return to_str(os.environ.get("SIGNUP_TOKEN_TYPE", "signup"))

    @property
    def SIGNUP_TOKEN_AGE(self):
        return to_int(os.environ.get("SIGNUP_TOKEN_AGE", "3600"))  # 1 hour

    @property
    def SIGNUP_URL(self):
        return to_str(
            os.environ.get("SIGNUP_URL", "http://localhost:3000/accounts/signup")
        )

    @property
    def PASSWD_TOKEN_TYPE(self):
        return to_str(os.environ.get("PASSWD_TOKEN_TYPE", "passwd"))

    @property
    def PASSWD_TOKEN_AGE(self):
        return to_int(os.environ.get("PASSWD_TOKEN_AGE", "3600"))  # 1 hour

    @property
    def PASSWD_URL(self):
        return to_str(
            os.environ.get(
                "PASSWD_URL", "http://localhost:3000/accounts/me/password-reset"
            )
        )

    @property
    def USE_GRAPHQL(self):
        return to_bool(os.environ.get("USE_GRAPHQL", "True"))

    @property
    def GQL_CONNECTION_LIMIT(self):
        return to_int(os.environ.get("GQL_CONNECTION_LIMIT", "50"))

    @property
    def GQL_MAX_SIZE(self):
        return to_int(os.environ.get("GQL_MAX_SIZE", "2048"))

    @property
    def GQL_MAX_DEFINITIONS(self):
        return to_int(os.environ.get("GQL_MAX_DEFINITIONS", "10"))

    @property
    def GQL_MAX_DEPTH(self):
        return to_int(os.environ.get("GQL_MAX_DEPTH", "10"))

    @property
    def GQL_MAX_FIELDS(self):
        return to_int(os.environ.get("GQL_MAX_FIELDS", "2"))

    @property
    def GQL_INTROSPECTION(self):
        return to_bool(os.environ.get("GQL_INTROSPECTION", "True"))

    @property
    def GQL_GRAPHIQL(self):
        return to_bool(os.environ.get("GQL_GRAPHIQL", "True"))

    @property
    def USE_ADMIN_SITE(self):
        return to_bool(os.environ.get("USE_ADMIN_SITE", "False"))

    @property
    def USE_DRF(self):
        return to_bool(os.environ.get("USE_DRF", "False"))

    @property
    def DRF_SWAGGER(self):
        return to_bool(os.environ.get("DRF_SWAGGER", "True"))

    @property
    def USE_DUMMY(self):
        return to_bool(os.environ.get("USE_DUMMY", "False"))

    @property
    def SESSION_ENGINE(self):
        return to_str(os.environ.get("SESSION_ENGINE", "db"))

    def __repr__(self):
        return f'<Props "{__name__}">'


props = Props()
