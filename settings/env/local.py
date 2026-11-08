from settings import conf
from settings.base import *
from settings.base import BASE_DIR

DEBUG = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "dbsqlite3",
    }
}

# Set BLOG_SQL_LOGGING=True in settings/.env to print every SQL query to the console.
if conf.SQL_LOGGING:
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {"console": {"class": "logging.StreamHandler"}},
        "loggers": {
            "django.db.backends": {"handlers": ["console"], "level": "DEBUG"},
        },
    }
