from __future__ import absolute_import

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedreader.settings_local')

from django.conf import settings

app = Celery('feedreader',
             broker='amqp://',
             backend='amqp://',
             include=['feedreader.tasks'])


# Using a string here means the worker will not have to
# pickle the object when using Windows.
app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


if __name__ == '__main__':
    app.start()
