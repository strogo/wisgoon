import os
from datetime import datetime
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedreader.settings')

app = Celery('tasks', broker='amqp://guest@79.127.125.146//')
app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']

from django.db.models import F

from pin.model_mongo import Notif, MonthlyStats, NotifCount
from pin.models import Post, Follow

from user_profile.models import Profile
# from pin.my_notif import NotifCas


@app.task(name="tasks.notif_test")
def notif_send(user_id, type, post, actor_id, seen=False, post_image=None):
    NotifCount.objects(owner=user_id).update_one(inc__unread=1, upsert=True)

    Notif.objects.create(owner=user_id, type=type, post=post,
                         last_actor=actor_id,
                         date=datetime.now,
                         post_image=post_image)
    # Notif.objects.create(owner=user_id, type=type, post=post,
    #                      last_actor=actor_id,
    #                      date=datetime.now,
    #                      seen=False,
    #                      post_image=post_image,
    #                      actors=[actor_id])

    # Notif.objects(owner=user_id, type=type, post=post)\
    #     .update_one(set__last_actor=actor_id,
    #                 set__date=datetime.now,
    #                 set__seen=False,
    #                 set__post_image=post_image,
    #                 add_to_set__actors=actor_id, upsert=True)

    # n = NotifCas.objects.filter(owner=user_id, type=type, post=post)\
    #     .update(seen=False, actors__prepend=[actor_id], date=datetime.now(),
    #             post_image=post_image, last_actor=actor_id)

    # print "notif type:", n

    return "hello notif"


@app.task(name="tasks.inc_prof")
def inc_prof(user_id):
    print "inc_prof", user_id


@app.task(name="tasks.profile_after_like")
def profile_after_like(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') + 1, score=F('score') + 10)

    MonthlyStats.log_hit(object_type=MonthlyStats.LIKE)

    return "after like"


@app.task(name="tasks.profile_after_dislike")
def profile_after_dislike(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') - 1, score=F('score') - 10)

    return "after dislike"


@app.task(name="tasks.clear_notif")
def clear_notif(user_id):
    Notif.objects.filter(owner=user_id).order_by('-date')[100:].delete()
    print "clear notif"
    return "clear botif"


@app.task(name="tasks.post_to_followers")
def post_to_followers(user_id, post_id):
    # Get the users follow owner of post
    followers = Follow.objects.filter(following_id=user_id)\
        .values_list('follower_id', flat=True)
    # print followers
    for follower_id in followers:
        # print follower
        try:
            Post.add_to_user_stream(post_id=post_id, user_id=follower_id)
        except Exception, e:
            print str(e)
            pass

    print "post to followers"
    return "post to followers"
