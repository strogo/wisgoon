# -*- coding: utf-8 -*-
from settings_local import *
# from django.db import connections

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False

# TEMPLATE_DIRS = (
#     os.path.join(SITE_ROOT, 'templates'),
# )
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

IMAGE_CACHE_ROOT = os.path.join(MEDIA_ROOT, 'image_cache')
COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT

ADMINS = (
    ('bugs', 'bugs@wisgoon.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'root',
        'PASSWORD': '-)**Z{QT',
        'HOST': '79.127.125.146',
        'PORT': '',
    },
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'root',
        'PASSWORD': '-)**Z{QT',
        'HOST': '79.127.125.104',
        'PORT': '',
    }
}

CACHES = {
    'default': dict(
        BACKEND='johnny.backends.memcached.MemcachedCache',
        # LOCATION=['127.0.0.1:11211'],
        LOCATION=['79.127.125.104:11211'],
        JOHNNY_CACHE=True,
    )
}

# DATABASE_ROUTERS = ['pin.MasterSlaveRouter']

ALLOWED_HOSTS = ['www.wisgoon.com', '*.wisgoon.com',
                 'api.wisgoon.com',
                 'wisgoon.com', "Sib-DL2", "127.0.0.1:3060",
                 "127.0.0.1:3061", "127.0.0.1:3062", "127.0.0.1"]
EMAIL_HOST = "wisgoon.com"
DEFAULT_FROM_EMAIL = "info@wisgoon.com"

EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.wisgoon.com'
EMAIL_HOST_USER = 'info@wisgoon.com'
EMAIL_HOST_PASSWORD = '-)**Z{QT'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'wis_cac2'

USE_CELERY = False

SESSION_COOKIE_DOMAIN = '.wisgoon.com'
import warnings
import exceptions
warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter']

SITE_URL = 'http://www.wisgoon.com'
API_URL = "http://api.wisgoon.com"

MEDIA_PREFIX = 'http://media.wisgoon.com'

ENABLE_CACHING = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://79.127.125.146:8080/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}
SITE_NAME_FA = 'ویسگون'
SITE_NAME_EN = 'wisgoon'
SITE_URL_NAME = 'wisgoon.com'
SITE_DESC = 'what is going on, social image sharing'
