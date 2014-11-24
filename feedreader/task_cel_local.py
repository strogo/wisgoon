import os
from datetime import datetime
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedreader.settings_local')

app = Celery('tasks', broker='amqp://guest@localhost//')
app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

from django.db.models import F

from pin.model_mongo import Notif
from pin.models import Post
from pin.models_graph import PostGraph, UserGraph

from user_profile.models import Profile


@app.task(name="tasks.notif_test")
def notif_send(user_id, type, post, actor_id, seen=False):
    print "we are in notif_send"
    Notif.objects(owner=user_id, type=type, post=post)\
        .update_one(set__last_actor=actor_id,
                    set__date=datetime.now,
                    set__seen=False,
                    add_to_set__actors=actor_id, upsert=True)

    if type == 1:
        try:
            post = Post.objects.get(id=int(post))
        except:
            return "eee chera?"
        post_node = PostGraph.get_or_create(post_obj=post)
        user_node = UserGraph.get_or_create(user_id=actor_id)

        PostGraph.like(user_id=user_node, post_id=post_node)

    print "notif_test"
    return "hello notif"


@app.task(name="tasks.inc_prof")
def inc_prof(user_id):
    print "inc_prof", user_id


@app.task(name="tasks.profile_after_like")
def profile_after_like(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') + 1, score=F('score') + 10)
    print "after like"
    return "after like"


@app.task(name="tasks.profile_after_dislike")
def profile_after_dislike(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') - 1, score=F('score') - 10)

    print "after dislike"
    return "after dislike"
