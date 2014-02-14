from __future__ import absolute_import

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedreader.settings')

app = Celery('pin', broker='redis://localhost:6379/6', include=['pin.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES = 60,
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml'],
    CELERY_ANNOTATIONS = {'tasks.send_notif': {'rate_limit': '1/s'}},
    CELERY_DEFAULT_RATE_LIMIT = '5/s'
)

if __name__ == '__main__':
    app.start()
