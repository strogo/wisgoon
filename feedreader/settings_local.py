import os
DEBUG = True
THUMBNAIL_DEBUG = False
TEMPLATE_DEBUG = DEBUG
REPORT_TYPE = {'PIN':1,'COMMENT':2,'RSS':3}
SITE_ROOT = os.path.dirname(__file__)
ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)
MANAGERS = ADMINS
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'feedreader',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': 'somaye',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}
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
MEDIA_ROOT = os.path.join(SITE_ROOT,'media')
MEDIA_URL = '/media/'
STATIC_ROOT = os.path.join(SITE_ROOT,'statics')
STATIC_URL = '/static/'

IMAGE_CACHE_ROOT = os.path.join(MEDIA_ROOT,'image_cache')

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    #os.path.join(STATIC_ROOT,'stat'),
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
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'django.contrib.flatpages.middleware.FlatpageFallbackMiddleware',
    #'django_cprofile_middleware.middleware.ProfilerMiddleware',
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
    #'django.contrib.sitemaps',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.humanize',
    #'cacheops',
    #'rss',
    'pin',
    'registration',
    'south',
    'debug_toolbar',
    'sorl.thumbnail',
    'social_auth',
    'django.contrib.flatpages',
    'django.contrib.comments',
    #'djangosphinx',
    'daddy_avatar',
    #'ban',
    #'socialacc',
    'contactus',
    'compressor',
    'taggit',
    'user_profile',
    'captcha',
    #'google_contacts',
    'devserver',
    'tastypie',
)
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
ACCOUNT_ACTIVATION_DAYS = 7
LOGIN_REDIRECT_URL = '/'
INTERNAL_IPS = ('127.0.0.1',)
DEBUG_TOOLBAR_PANELS = (
    'debug_toolbar.panels.version.VersionDebugPanel',
    'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    'debug_toolbar.panels.signals.SignalDebugPanel',
    'debug_toolbar.panels.logger.LoggingPanel',
)

CACHES = {
    'default' : dict(
        #BACKEND = 'johnny.backends.memcached.MemcachedCache',
        BACKEND= 'django.core.cache.backends.memcached.MemcachedCache',
        LOCATION = ['127.0.0.1:11211'],
        #JOHNNY_CACHE = True,
    )
}

CACHEOPS_REDIS = {
    'host': 'localhost', # redis-server is on same machine
    'port': 6379,        # default redis port
    'db': 5,             # SELECT non-default redis database
                         # using separate redis db or redis instance
                         # is highly recommended
    'socket_timeout': 3,
}
CACHEOPS = {
    'auth.user': ('get', 60*15),
    'pin.category': ('all', 60*60),
    'pin.post': ('all', 60),
    #'pin.post': ('count', 60*60*60),
    'social_auth.usersocialauth': ('all', 60),
    'django.flatpage': ('all', 60*60*60),
    'taggit.tag': ('all', 60*60),
    'pin.comments': ('all', 60),
    'pin.likes': ('all', 60),
    '*.*': ('count', 60),
}

SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_myproj2'
SPHINX_SERVER = 'localhost'
SPHINX_PORT = 9312
COMPRESS_URL = MEDIA_URL
COMPRESS_ROOT = MEDIA_ROOT
COMPRESS_OUTPUT_DIR = 'static_cache'
NODE_URL='http://127.0.0.1:1312/'
API_LIMIT_PER_PAGE = 10
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}
