# -*- coding: utf-8 -*-
from settings_local import *

INSTANCE_NAME = 'jupiter'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False

# TEMPLATE_DIRS = (
#     os.path.join(SITE_ROOT, 'templates'),
# )
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')

STATIC_DOMAIN = "http://static.wisgoon.com/"

IMAGE_CACHE_ROOT = os.path.join(MEDIA_ROOT, 'image_cache')
COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT

ADMINS = (
    ('bugs', 'bugs@wisgoon.com'),
)

CASSANDRA_DB = '79.127.125.104'

COMPRESS_OUTPUT_DIR = '{}_cache'.format(INSTANCE_NAME)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'root',
        'PASSWORD': '-)**Z{QT',
        'HOST': '79.127.125.104',
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
        LOCATION=['79.127.125.99:11211'],
        JOHNNY_CACHE=True,
    ),
    'cache_layer': dict(
        BACKEND='django.core.cache.backends.memcached.MemcachedCache',
        LOCATION=['79.127.125.98:11211'],
    )
}

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://79.127.125.106:8080/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}

# DATABASE_ROUTERS = ['pin.MasterSlaveRouter']

ALLOWED_HOSTS = ['www.wisgoon.com', '*.wisgoon.com', 'wisgoon.com', "Sib-DL2", "127.0.0.1:3060", "127.0.0.1:3061", "127.0.0.1:3062", "127.0.0.1"]
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

CELERY_ROUTES = {
    'wisgoon.pin.add_to_storage': {
        'queue': 'add_storage_%s' % INSTANCE_NAME,
    },
    'wisgoon.pin.add_avatar_to_storage': {
        'queue': 'add_avatar_to_storage_%s' % INSTANCE_NAME,
    },
    'wisgoon.pin.migrate_avatar_storage': {
        'queue': 'migrate_avatar_storage_%s' % INSTANCE_NAME,
    },
    'wisgoon.pin.post_to_followers': {
        'queue': 'wisgoon.push.to.followers'
    },
    'wisgoon.pin.post_to_follower_single': {
        'queue': 'wisgoon.push.follower'
    },
    'wisgoon.pin.check_porn': {
        'queue': 'wisgoon.pin.check_porn'
    }
}
