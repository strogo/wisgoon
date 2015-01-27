from settings_local import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False

ADMINS = (
    ('support', 'support@wisgoon.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'root',
        'PASSWORD': '-)**Z{QT',
        'HOST': 'localhost',
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['www.wisgoon.com', '*.wisgoon.com', 'wisgoon.com']
EMAIL_HOST = "wisgoon.com"
DEFAULT_FROM_EMAIL = "info@wisgoon.com"

EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.wisgoon.com'
EMAIL_HOST_USER = 'info@wisgoon.com'
EMAIL_HOST_PASSWORD = '-)**Z{QT'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'wis_cac2'

USE_CELERY = True

SESSION_COOKIE_DOMAIN = '.wisgoon.com'
import warnings
import exceptions
warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter']

SITE_URL = 'http://www.wisgoon.com'

MEDIA_PREFIX = 'http://media.wisgoon.com'

ENABLE_CACHING = True