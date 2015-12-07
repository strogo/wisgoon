# -*- coding: utf-8 -*-
import os
# from easy_thumbnails.conf import Settings as thumbnail_settings

INSTANCE_NAME = 'moon'
DEBUG = True
THUMBNAIL_DEBUG = True
TEMPLATE_DEBUG = DEBUG
REPORT_TYPE = {'PIN': 1, 'COMMENT': 2, 'RSS': 3}
STATIC_VERSION = '5.7.88'
SITE_ROOT = os.path.dirname(__file__)
ADMINS = (
    ('bugs', 'bugs@wisgoon.com'),
)

CASSANDRA_DB = '127.0.0.1'

# THUMBNAIL_PROCESSORS = (
#     'image_cropping.thumbnail_processors.crop_corners',
# ) + thumbnail_settings.THUMBNAIL_PROCESSORS

ALLOWED_HOSTS = ["127.0.0.1:8000",
                 "192.168.0.110:8080"
                 "127.0.0.1",
                 "127.0.0.1:3060",
                 "127.0.0.1:3061",
                 "127.0.0.1:3062"]
MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'root',
        'PASSWORD': 'somaye',
        'HOST': 'wisgoon.db',
        'PORT': '',
    },
    'slave': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'root',
        'PASSWORD': 'somaye',
        'HOST': 'wisgoon.db',
        'PORT': '',
    }
}

REDIS_DB = 'wisgoon.db'
REDIS_DB_NUMBER = 11

REDIS_DB_2 = 'wisgoon.db.2'
REDIS_DB_NUMBER_2 = 10

MONGO_DB = "wisgoon"
MONGO_DB_HOST = "wisgoon.mongo.db"

GOOGLE_COOKIE_CONSENT = 'google_token_consent'
GOOGLE_REDIRECT_SESSION_VAR = 'google_contacts_redirect'
GOOGLE_REDIRECT_BASE_URL = 'http://localhost:8000'
EMAIL_HOST = "mail.wisgoon.com"
TIME_ZONE = 'Asia/Tehran'
LANGUAGE_CODE = 'fa-ir'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(SITE_ROOT, 'statics')
STATIC_URL = '/static/'

THUMBNAIL_PREFIX = 'cache2/'
THUMBNAIL_KVSTORE = 'sorl.thumbnail.kvstores.cached_db_kvstore.KVStore'
# THUMBNAIL_QUALITY = 90

IMAGE_CACHE_ROOT = os.path.join(MEDIA_ROOT, 'image_cache')

TASTYPIE_DEFAULT_FORMATS = ['json']

API_LIMIT_PER_PAGE = 10
API_THUMB_QUALITY = 99

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # os.path.join(STATIC_ROOT,'stat'),
)
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
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
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'johnny.middleware.LocalStoreClearMiddleware',
    # 'johnny.middleware.QueryCacheMiddleware',
    'pin.middleware.UrlRedirectMiddleware',
    'pin.middleware.XsSharing',
    # 'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    # 'django_cprofile_middleware.middleware.ProfilerMiddleware',
)
CACHE_MIDDLEWARE_ANONYMOUS_ONLY = True
ROOT_URLCONF = 'feedreader.urls_local'
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
    # 'social_auth.context_processors.social_auth_by_name_backends',
    # 'social_auth.context_processors.social_auth_backends',
    # 'social_auth.context_processors.social_auth_by_type_backends',
    # 'social_auth.context_processors.social_auth_login_redirect',
    # 'rss.context_processors.c_url',
    # 'rss.context_processors.node_url',
    'pin.context_processors.pin_form',
    'pin.context_processors.pin_categories',
    'pin.context_processors.is_super_user',
    'pin.context_processors.user__id',
    'pin.context_processors.today_stats',
    'pin.context_processors.media_prefix',
    'pin.context_processors.is_police',
    'pin.context_processors.subs',
    'pin.context_processors.global_values',
    'pin.context_processors.static_version',
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

    'haystack',
    # 'easy_thumbnails',
    # 'image_cropping',
    # 'feedreader',
    'blog',
    'pin',
    'registration',
    'south',
    'sorl.thumbnail',
    # 'social_auth',
    'django.contrib.comments',
    'daddy_avatar',
    'contactus',
    'compressor',
    # 'taggit',
    'user_profile',
    'captcha',
    'tastypie',
    # 'devserver',
    # 'debug_toolbar',
    'widget_tweaks',
    'ckeditor',
)

HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.solr_backend.SolrEngine',
        'URL': 'http://127.0.0.1:8983/solr'
        # ...or for multicore...
        # 'URL': 'http://127.0.0.1:8983/solr/mysite',
    },
}

AUTHENTICATION_BACKENDS = (
    # 'social_auth.backends.twitter.TwitterBackend',
    # 'social_auth.backends.facebook.FacebookBackend',
    # 'social_auth.backends.google.GoogleOAuthBackend',
    # 'social_auth.backends.google.GoogleOAuth2Backend',
    # 'social_auth.backends.google.GoogleBackend',
    # 'social_auth.backends.yahoo.YahooBackend',
    # 'social_auth.backends.contrib.yahoo.YahooOAuthBackend',
    'django.contrib.auth.backends.ModelBackend',
)

CKEDITOR_UPLOAD_PATH = "ckeditor_uploads/"
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
    },
}

# DEBUG_TOOLBARN_CONFIG = {
#     'INTERCEPT_REDIRECTS': True,
# }

SOCIAL_AUTH_ASSOCIATE_BY_MAIL = True

ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = '/'

INTERNAL_IPS = ('127.0.0.1',)
# DEBUG_TOOLBAR_PANELS = (
#     'debug_toolbar.panels.version.VersionDebugPanel',
#     'debug_toolbar.panels.timer.TimerDebugPanel',
#     'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
#     'debug_toolbar.panels.headers.HeaderDebugPanel',
#     'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
#     'debug_toolbar.panels.template.TemplateDebugPanel',
#     'debug_toolbar.panels.sql.SQLDebugPanel',
#     'debug_toolbar.panels.signals.SignalDebugPanel',
#     'debug_toolbar.panels.logger.LoggingPanel',
# )

CACHES = {
    'default': dict(
        # BACKEND='johnny.backends.memcached.MemcachedCache',
        BACKEND='django.core.cache.backends.memcached.MemcachedCache',
        LOCATION=['127.0.0.1:11211'],
        # LOCATION=['79.127.125.104:11211'],
        # JOHNNY_CACHE=False,
    )
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db'
JOHNNY_MIDDLEWARE_KEY_PREFIX = 'wis_cac2'

COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT
COMPRESS_OUTPUT_DIR = 'static_cache'

FACEBOOK_APP_ID = 242648675868616
FACEBOOK_APP_SECRET = '459f3ab2b3ccd33e1f0eef65c0dfcfcd'
FACEBOOK_REGISTRATION_BACKEND = 'registration.backends.default.DefaultBackend'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': "[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s",
            'datefmt': "%d/%b/%Y %H:%M:%S"
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        },
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'mail_admins'],
            'propagate': True,
            'level': 'WARN',
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
    }
}

STREAM_LATEST = 'list_latest'
STREAM_LATEST_CAT = 'list_latest_cat'

USER_STREAM = "user_stream2"

LAST_LIKES = 'list_last_likes'
USER_LAST_LIKES = 'userlast_likes'

POST_LIKERS = "wis_likers_2_"
USER_NAME_CACHE = "un_"

HOME_STREAM = "home_stream"

PENDINGS = "pengings"

LIST_LONG = 5000

LIKE_WITH_CELERY = False

USE_CELERY = False
USE_CELERY_V2 = True
USE_CELERY_V3 = True

APP_TOKEN_STR = 'app mobile-)**Z{QT'
APP_TOKEN_KEY = 'e622c330c77a17c8426e638d7a85da6c2ec9f455'

# USE_THOUSAND_SEPARATOR = True
# THOUSAND_SEPARATOR = ','
# DECIMAL_SEPARATOR = ','
# NUMBER_GROUPING = 3

HAYSTACK_SIGNAL_PROCESSOR = 'pin.signals.MySignalProcessor'

COMPRESS_CSS_FILTERS = [
    'compressor.filters.css_default.CssAbsoluteFilter',
    'compressor.filters.cssmin.CSSMinFilter']

SITE_URL = 'http://127.0.0.1:8000'

API_URL = "http://127.0.0.1:8000"

MEDIA_PREFIX = 'http://127.0.0.1:8000'

MERCHANT_ID = '54c4fa4c-3458-409d-8f01-47d55bef37d4'

ENABLE_CACHING = False

CORS_URLS_REGEX = r'^/pin/api/.*$'

SITE_NAME_FA = 'ویسگون'
SITE_NAME_EN = 'wisgoon'
SITE_URL_NAME = 'wisgoon.com'
SITE_DESC = 'what is going on, social image sharing'

STREAM_CASSANDRA_HOSTS = 'localhost'


SCORE_FOR_COMMENING = 0
SCORE_FOR_STREAMS = 0

# CELERY_ALWAYS_EAGER = True

BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tehran'
CELERY_IGNORE_RESULT = True
SITE_ID = 1

CELERY_ENABLE_UTC = True

CELERY_ROUTES = {
    'wisgoon.pin.say_salam': {
        'queue': 'feeds'
    }
}

# format of avatar cache name by user_id
AVATAR_CACHE_KEY = "dad:avatar:{}"
