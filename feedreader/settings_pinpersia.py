from settings_local import *
# from django.db import connections

DEBUG = False
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False

TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates_pinpersia'),
)
MEDIA_ROOT = os.path.join(SITE_ROOT, 'pinpersia_media')

IMAGE_CACHE_ROOT = os.path.join(MEDIA_ROOT, 'image_cache')
COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT

ADMINS = (
    ('bugs', 'bugs@pinpersia.com'),
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'pinpersia_db',
        'USER': 'root',
        'PASSWORD': '-)**Z{QT',
        'HOST': 'localhost',
        'PORT': '',
    }
}

REDIS_DB = '127.0.0.1'
REDIS_DB_NUMBER = 13

MONGO_DB = "pinpersia"
MONGO_DB_HOST = "127.0.0.1"

CACHES = {
    'default': dict(
        BACKEND='johnny.backends.memcached.MemcachedCache',
        #LOCATION=['127.0.0.1:11211'],
        LOCATION=['79.127.125.104:11211'],
        JOHNNY_CACHE=True,
        KEY_PREFIX='pinpersia',
    )
}

# DATABASE_ROUTERS = ['pin.MasterSlaveRouter']

ALLOWED_HOSTS = ["127.0.0.1:3060",
                 "127.0.0.1:3061",
                 "127.0.0.1:3062",
                 "127.0.0.1",
                 "pinpersia.com",
                 "*.pinpersia.com",
                 "www.pinpersia.com"]

EMAIL_HOST = "pinpersia.com"
DEFAULT_FROM_EMAIL = "info@pinpersia.com"

EMAIL_USE_TLS = True
EMAIL_HOST = 'mail.pinpersia.com'
EMAIL_HOST_USER = 'info@pinpersia.com'
EMAIL_HOST_PASSWORD = '-)**Z{QT'

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'pinpersia_cac2'

USE_CELERY = False

SESSION_COOKIE_DOMAIN = '.pinpersia.com'
import warnings
import exceptions
warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning)

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter']

SITE_URL = 'http://www.pinpersia.com'

MEDIA_PREFIX = 'http://media.pinpersia.com'

ENABLE_CACHING = True

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr/pinpersia'
        # 'URL': 'http://79.127.125.146:8080/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}
