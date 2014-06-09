import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedreader.settings_local')

app = Celery('tasks', broker='amqp://guest@localhost//')
app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

@app.task(name="tasks.notif_test")
def notif_test():
    print "notif_test"
