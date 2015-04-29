from settings_local import *
# from django.db import connections

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates_emsham'),
)
MEDIA_ROOT = os.path.join(SITE_ROOT, 'emsham_media')

IMAGE_CACHE_ROOT = os.path.join(MEDIA_ROOT, 'image_cache')
COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT

ADMINS = (
    ('bugs', 'bugs@emsham.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'emsham_db',
        'USER': 'root',
        'PASSWORD': '-)**Z{QT',
        'HOST': 'localhost',
        'PORT': '',
    }
}

REDIS_DB = '127.0.0.1'
REDIS_DB_NUMBER = 12

MONGO_DB = "emsham"
MONGO_DB_HOST = "127.0.0.1"

CACHES = {
    'default': dict(
        BACKEND='johnny.backends.memcached.MemcachedCache',
        #LOCATION=['127.0.0.1:11211'],
        LOCATION=['79.127.125.104:11211'],
        JOHNNY_CACHE=True,
        KEY_PREFIX='emsham',
    )
}

# DATABASE_ROUTERS = ['pin.MasterSlaveRouter']

ALLOWED_HOSTS = ['www.emsham.ir',
                 '*.emsham.ir',
                 'emsham.ir',
                 "Sib-DL2",
                 "127.0.0.1:3060",
                 "127.0.0.1:3061",
                 "127.0.0.1:3062",
                 "127.0.0.1",
                 "emsham.com",
                 "*.emsham.com",
                 "www.emsham.com"]

EMAIL_HOST = "emsham.com"
DEFAULT_FROM_EMAIL = "info@emsham.com"

EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.emsham.com'
EMAIL_HOST_USER = 'info@emsham.com'
EMAIL_HOST_PASSWORD = '-)**Z{QT'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'sham_cac2'

USE_CELERY = False

SESSION_COOKIE_DOMAIN = '.emsham.com'
import warnings
import exceptions
warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter']

SITE_URL = 'http://www.emsham.com'

MEDIA_PREFIX = 'http://media.emsham.com'

ENABLE_CACHING = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr'
        # 'URL': 'http://79.127.125.146:8080/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}
