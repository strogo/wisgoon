# -*- coding: utf-8 -*-
from settings_production import *

INSTANCE_NAME = 'saturn'

COMPRESS_OUTPUT_DIR = '{}_cache'.format(INSTANCE_NAME)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'feedreader',
        'USER': 'wis_db_user',
        'PASSWORD': 'OTEfiD6aNeQ4E',
        'HOST': '79.127.125.99',
        'PORT': '',
    }
}

CELERY_ROUTES = {
    'wisgoon.pin.post_to_followers': {
        'queue': 'wisgoon.push.to.followers'
    },
    'wisgoon.pin.post_to_follower_single': {
        'queue': 'wisgoon.push.follower'
    },
    'wisgoon.pin.check_porn': {
        'queue': 'wisgoon.pin.check_porn'
    },
    'wisgoon.pin.activity': {
        'queue': 'wisgoon.pin.activity'
    },
    'wisgoon.analytics.tick': {
        'queue': 'wisgoon.analytics.tick'
    },
    'wisgoon.pin.porn_feedback': {
        'queue': 'wisgoon.pin.porn_feedback'
    },
    'wisgoon.pin.add_to_storage': {
        'queue': 'add_storage_%s' % INSTANCE_NAME,
    },
    'wisgoon.pin.add_avatar_to_storage': {
        'queue': 'add_avatar_to_storage_%s' % INSTANCE_NAME,
    },
    'wisgoon.pin.migrate_avatar_storage': {
        'queue': 'migrate_avatar_storage_%s' % INSTANCE_NAME,
    },
}
