import os
DEBUG = True
TEMPLATE_DEBUG = DEBUG
THUMBNAIL_DEBUG = False
REPORT_TYPE = {'PIN': 1, 'COMMENT': 2, 'RSS': 3}
SITE_ROOT = os.path.dirname(__file__)
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'root',
        'PASSWORD': '-)**Z{QT',
        'HOST': '',
        'PORT': '',
    }
}
ALLOWED_HOSTS = ['www.wisgoon.com', '*.wisgoon.com', 'wisgoon.com']
EMAIL_HOST = "wisgoon.com"
DEFAULT_FROM_EMAIL = "info@wisgoon.com"
TIME_ZONE = 'Asia/Tehran'
LANGUAGE_CODE = 'fa-ir'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = ''
ACCOUNT_ACTIVATION_DAYS = 7
STATIC_URL = '/statics/'
STATICFILES_DIRS = ()
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder'
)
SECRET_KEY = 'iqeri28py6po$@c2a#dvicdqh7)58%!17jdou=7-$su#w5i6m)'
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
    #'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
)
ROOT_URLCONF = 'feedreader.urls'
WSGI_APPLICATION = 'feedreader.wsgi.application'
TEMPLATE_DIRS = (
    os.path.join(SITE_ROOT, 'templates'),
)
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
    'social_auth.context_processors.social_auth_by_name_backends',
    'social_auth.context_processors.social_auth_backends',
    'social_auth.context_processors.social_auth_by_type_backends',
    'social_auth.context_processors.social_auth_login_redirect',
    #'rss.context_processors.c_url',
    #'rss.context_processors.node_url',
    'pin.context_processors.pin_form',
    'pin.context_processors.pin_categories',
    'pin.context_processors.is_super_user',
    'pin.context_processors.user__id',
)
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    #'cacheops',
    #'rss',
    'pin',
    'registration',
    'south',
    #'debug_toolbar',
    'social_auth',
    #'django.contrib.flatpages',
    'django.contrib.comments',
    'sorl.thumbnail',
    'djangosphinx',
    'daddy_avatar',
    #'cacheops',
    #'socialacc',
    'contactus',
    'compressor',
    'taggit',
    'user_profile',
    'tastypie',
    'captcha',
)

CACHEOPS_REDIS = {
    'host': 'localhost',
    'port': 6379,
    'db': 5,
    'socket_timeout': 3,
}
CACHEOPS = {
    'auth.user': ('get', 60 * 15),
    'pin.category': ('all', 60 * 15),
    'social_auth.usersocialauth': ('all', 60),
    'pin.post': ('count', 60),
    'django.flatpage': ('all', 60),
    'taggit.tag': ('all', 60),
    #'pin.comments': ('all', 60),
    'pin.likes': ('all', 60),
    'pin.notif': ('all', 60),
    'user_profile.profile': ('all', 60),
    '*.*': ('count', 60),
}
AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'social_auth.backends.google.GoogleOAuthBackend',
    'social_auth.backends.google.GoogleOAuth2Backend',
    'social_auth.backends.google.GoogleBackend',
    'social_auth.backends.yahoo.YahooBackend',
    'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)
SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True
ACCOUNT_EMAIL_REQUIRED = True
LOGIN_REDIRECT_URL = '/'

CACHES = {
    'default': dict(
        BACKEND = 'johnny.backends.memcached.MemcachedCache',
        #BACKEND = 'django.core.cache.backends.memcached.MemcachedCache',
        LOCATION = ['127.0.0.1:11211'],
        JOHNNY_CACHE = True,
    )
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
JOHNNY_MIDDLEWARE_KEY_PREFIX='wis_cac2'
SPHINX_SERVER = 'localhost'
SPHINX_PORT = 9312
#THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.redis_kvstore.KVStore'
#THUMBNAIL_REDIS_HOST = 'localhost'
#THUMBNAIL_REDIS_PORT = 6379
THUMBNAIL_PREFIX = 'cache2/'
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'

COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT
COMPRESS_OUTPUT_DIR = 'static_cache'
FACEBOOK_APP_ID = 242648675868616
FACEBOOK_APP_SECRET = '459f3ab2b3ccd33e1f0eef65c0dfcfcd'
FACEBOOK_REGISTRATION_BACKEND = 'registration.backends.default.DefaultBackend'
NODE_URL='http://www.wisgoon.com:1312/'
API_LIMIT_PER_PAGE = 10
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format' : "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt' : "%d/%b/%Y %H:%M:%S"
        },
    },
    'handlers': {
        'null': {
            'level':'DEBUG',
            'class':'django.utils.log.NullHandler',
        },
        'logfile': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': SITE_ROOT + "/logfile",
            'maxBytes': 50000,
            'backupCount': 2,
            'formatter': 'standard',
        },
        'console':{
            'level':'INFO',
            'class':'logging.StreamHandler',
            'formatter': 'standard'
        },
    },
    'loggers': {
        'django': {
            'handlers':['console'],
            'propagate': True,
            'level':'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'pin': {
            'handlers': ['console', 'logfile'],
            'level': 'DEBUG',
        },
    }
}
SESSION_COOKIE_DOMAIN = '.wisgoon.com'
import warnings
import exceptions
warnings.filterwarnings("ignore", category=exceptions.RuntimeWarning)
