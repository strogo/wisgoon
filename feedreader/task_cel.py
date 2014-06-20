import os
from datetime import datetime
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedreader.settings')

app = Celery('tasks', broker='amqp://guest@localhost//')
app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

from django.db.models import F

from pin.model_mongo import Notif

from user_profile.models import Profile

@app.task(name="tasks.notif_test")
def notif_send(user_id, type, post, actor_id, seen=False):
    Notif.objects(owner=user_id, type=type, post=post)\
        .update_one(set__last_actor=actor_id,
                    set__date=datetime.now,
                    set__seen=False,
                    add_to_set__actors=actor_id, upsert=True)

    return "hello notif"

@app.task(name="tasks.inc_prof", rate_limit=50/m)
def inc_prof(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like')+1, score=F('score')+10)
    
    return "inc prof"
