# -*- coding: utf-8 -*-
from settings_local import *
# from django.db import connections

DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False

# TEMPLATE_DIRS = (
#     os.path.join(SITE_ROOT, 'templates_emsham'),
# )
MEDIA_ROOT = os.path.join(SITE_ROOT, 'salam_media')

IMAGE_CACHE_ROOT = os.path.join(MEDIA_ROOT, 'image_cache')
COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT

ADMINS = (
    ('bugs', 'bugs@social.rabtcdn.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'salam_db',
        'USER': 'salam_usr',
        'PASSWORD': "nwpfZn4lzxgTQ",
        'HOST': 'localhost',
        'PORT': '',
    }
}

REDIS_DB = '127.0.0.1'
REDIS_DB_NUMBER = 12

MONGO_DB = "salam"
MONGO_DB_HOST = "127.0.0.1"

CACHES = {
    'default': dict(
        BACKEND='johnny.backends.memcached.MemcachedCache',
        LOCATION=['79.127.125.104:11211'],
        JOHNNY_CACHE=True,
        KEY_PREFIX='emsham',
    )
}

# DATABASE_ROUTERS = ['pin.MasterSlaveRouter']

ALLOWED_HOSTS = ["127.0.0.1",
                 "social.rabtcdn.com"]

EMAIL_HOST = "social.rabtcdn.com"
DEFAULT_FROM_EMAIL = "info@social.rabtcdn.com"

EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.social.rabtcdn.com'
EMAIL_HOST_USER = 'info@social.rabtcdn.com'
EMAIL_HOST_PASSWORD = '-)**Z{QT'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'sham_cac2'

USE_CELERY = False

SESSION_COOKIE_DOMAIN = '.social.rabtcdn.com'
import warnings
import exceptions
warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter']

SITE_URL = 'http://www.social.rabtcdn.com'

MEDIA_PREFIX = 'http://media.social.rabtcdn.com'

ENABLE_CACHING = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8080/solr/emsham'
        # 'URL': 'http://79.127.125.146:8080/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}
SITE_NAME_FA = 'امشام'
SITE_NAME_EN = 'emsham'
SITE_URL_NAME = 'social.rabtcdn.com'
SITE_DESC = 'what is going on, social image sharing'
