from __future__ import absolute_import

from celery import Celery

app = Celery('pin', broker='redis://localhost:6379/6', include=['pin.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
    CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml'],
)

if __name__ == '__main__':
    app.start()
