# -*- coding: utf-8 -*-
from settings_local import *

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False
DISPLAY_AD = True

MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

STATIC_DOMAIN = "http://static.wisgoon.com/"

IMAGE_CACHE_ROOT = os.path.join(MEDIA_ROOT, 'image_cache')
COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT

ADMINS = (
    ('bugs', 'bugs@wisgoon.com'),
)

CASSANDRA_DB = '79.127.125.104'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'wis_db_user',
        'PASSWORD': 'OTEfiD6aNeQ4E',
        'HOST': '79.127.125.99',
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
        BACKEND='django.core.cache.backends.memcached.MemcachedCache',
        LOCATION=['79.127.125.98:11211'],
    ),
    'cache_layer': dict(
        BACKEND='django.core.cache.backends.memcached.MemcachedCache',
        LOCATION=['79.127.125.98:11211'],
    )
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://79.127.125.146:8080/solr',
    },
}

ALLOWED_HOSTS = ['www.wisgoon.com', '*.wisgoon.com', 'wisgoon.com', "Sib-DL2",
                 "127.0.0.1:3060", "127.0.0.1:3061", "127.0.0.1:3062",
                 "127.0.0.1", "debian", "rokh01",
                 "wisweb1.com", "www.wisweb1.com",
                 "wisweb2.com", "www.wisweb2.com",
                 "wisweb3.com", "www.wisweb3.com"]

EMAIL_HOST = "wisgoon.com"
DEFAULT_FROM_EMAIL = "info@wisgoon.com"

EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.wisgoon.com'
EMAIL_HOST_USER = 'info@wisgoon.com'
EMAIL_HOST_PASSWORD = '-)**Z{QT'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'wis_cac2'

USE_CELERY = False
USE_CELERY_V2 = False

CELERY_IGNORE_RESULT = True

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

SCORE_FOR_COMMENING = -5000
SCORE_FOR_STREAMS = 10000

BROKER_URL = 'amqp://guest@79.127.125.98//'
CELERY_RESULT_BACKEND = 'amqp://guest@79.127.125.98//'

NEO4J_DATABASE = "http://79.127.125.98:7474/db/data/"

ES_HOST = "79.127.125.98"
INFLUX_HOST = "79.127.125.99"


REDIS_DB = '79.127.125.146'
REDIS_DB_NUMBER = 11

REDIS_DB_2 = '79.127.125.99'
REDIS_DB_NUMBER_2 = 10

REDIS_DB_3 = '79.127.125.98'
REDIS_DB_4 = '79.127.125.98'

STATIC_DOMAIN = "http://static.wisgoon.com"
STATIC_CDN = "http://static.wisgoon.com/media/assets/"

MONGO_DB_HOST = "79.127.125.98"
