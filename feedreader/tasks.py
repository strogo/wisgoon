from __future__ import absolute_import
from datetime import datetime

from django.db.models import F

from feedreader.celery import app
from pin.model_mongo import Notif, MonthlyStats, NotifCount
from pin.models import Post, Follow

from user_profile.models import Profile


@app.task()
def notif_send(user_id, type, post, actor_id, seen=False, post_image=None):
    NotifCount.objects(owner=user_id).update_one(inc__unread=1, upsert=True)

    Notif.objects.create(owner=user_id, type=type, post=post,
                         last_actor=actor_id,
                         date=datetime.now,
                         post_image=post_image)

    return "hello notif"


@app.task()
def inc_prof(user_id):
    print "inc_prof", user_id


@app.task()
def profile_after_like(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') + 1, score=F('score') + 10)

    MonthlyStats.log_hit(object_type=MonthlyStats.LIKE)
    print "after like"

    return "after like"


@app.task()
def profile_after_dislike(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') - 1, score=F('score') - 10)

    return "after dislike"


@app.task()
def clear_notif(user_id):
    Notif.objects.filter(owner=user_id).order_by('-date')[100:].delete()
    print "clear notif"
    return "clear botif"


@app.task()
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


@app.task
def add(x, y):
    return x + y


@app.task
def mul(x, y):
    return x * y


@app.task
def xsum(numbers):
    return sum(numbers)
