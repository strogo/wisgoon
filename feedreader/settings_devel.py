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
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'wis_db_user',
        'PASSWORD': 'OTEfiD6aNeQ4E',
        'HOST': '79.127.125.99',
        'PORT': '',
    },
    'postgres': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'wisgoon',
        'USER': 'wisgoon_user',
        'PASSWORD': 'KP9CPby8jkOCw',
        'HOST': '79.127.125.99',
        'PORT': '',
    },
}

ALLOWED_HOSTS = ALLOWED_HOSTS + ["new.wisgoon.com"]
