# -*- coding: utf-8 -*-
from settings_local import *

INSTANCE_NAME = 'mars'

COMPRESS_OUTPUT_DIR = '{}_cache'.format(INSTANCE_NAME)

CELERY_ROUTES.update({
    'wisgoon.pin.add_to_storage': {
        'queue': 'add_storage_%s' % INSTANCE_NAME,
    },
    'wisgoon.pin.add_avatar_to_storage': {
        'queue': 'add_avatar_to_storage_%s' % INSTANCE_NAME,
    },
    'wisgoon.pin.migrate_avatar_storage': {
        'queue': 'migrate_avatar_storage_%s' % INSTANCE_NAME,
    },
})
