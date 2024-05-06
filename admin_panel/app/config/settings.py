from split_settings.tools import include
import os

include(
    "components/middleware.py",
    "components/application.py",
    "components/templates.py",
    "components/database.py",
    "components/security.py",
)

LOCALE_PATHS = ["movies/locale"]
ROOT_URLCONF = "config.urls"
STATIC_URL = "static/"
STATIC_ROOT = os.environ.get('STATIC_ROOT')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT')

WSGI_APPLICATION = "config.wsgi.application"

LANGUAGE_CODE = "ru-RU"
TIME_ZONE = "Europe/Moscow"
USE_I18N = True
USE_TZ = True
