import logging
import os

if os.environ.get("USE_GEVENT", "").lower() == "true":
    try:
        from gevent.monkey import patch_all

        patch_all()
        from psycogreen.gevent import patch_psycopg

        patch_psycopg()
    except ImportError as e:
        logging.error("ImportError: %s", e)

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from conf.celery import app as celery_app
from conf.props import props

__all__ = (
    "celery_app",
    "props",
)
