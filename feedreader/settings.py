from settings_local import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'root',
        'PASSWORD': '-)**Z{QT',
        'HOST': '79.127.125.149',
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['www.wisgoon.com', '*.wisgoon.com', 'wisgoon.com']
EMAIL_HOST = "wisgoon.com"
DEFAULT_FROM_EMAIL = "info@wisgoon.com"

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'wis_cac2'

SESSION_COOKIE_DOMAIN = '.wisgoon.com'
import warnings
import exceptions
warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning)
