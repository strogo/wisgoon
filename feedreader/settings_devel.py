# -*- coding: utf-8 -*-
from settings_production import *

DEBUG = True
TEMPLATE_DEBUG = True
THUMBNAIL_DEBUG = False
DISPLAY_AD = True

SITE_ID = 2

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
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'wisgoon',
        'USER': 'wisgoon_user',
        'PASSWORD': 'KP9CPby8jkOCw',
        'HOST': '79.127.125.99',
        'PORT': '',
    }
}

ALLOWED_HOSTS = ['www.wisgoon.com', '*.wisgoon.com', 'wisgoon.com', "Sib-DL2",
                 "127.0.0.1:3060", "127.0.0.1:3061", "127.0.0.1:3062",
                 "127.0.0.1", "debian", "rokh01", "new.wisgoon.com",
                 "wisweb1.com", "www.wisweb1.com",
                 "wisweb2.com", "www.wisweb2.com",
                 "wisweb3.com", "www.wisweb3.com"]
