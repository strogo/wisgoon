import os
from celery import Celery

from django.db.models import F

from pin.model_mongo import MonthlyStats
from pin.models import Post, Follow

from user_profile.models import Profile
from pin.models_redis import NotificationRedis

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'feedreader.settings_local')

app = Celery('tasks', broker='amqp://guest@localhost//')
app.conf.CELERY_TASK_SERIALIZER = 'json'
app.conf.CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'msgpack', 'yaml']


@app.task(name="tasks.notif_test")
def notif_send(user_id, type, post, actor_id,
               seen=False, post_image=None, comment=None):
    NotificationRedis(user_id=user_id)\
        .set_notif(ntype=type, post=post, actor=actor_id, comment=comment)

    return "hello notif"


@app.task(name="tasks.inc_prof")
def inc_prof(user_id):
    print "inc_prof", user_id


@app.task(name="tasks.profile_after_like")
def profile_after_like(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') + 1, score=F('score') + 10)

    MonthlyStats.log_hit(object_type=MonthlyStats.LIKE)
    print "after like"

    return "after like"


@app.task(name="tasks.profile_after_dislike")
def profile_after_dislike(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') - 1, score=F('score') - 10)

    return "after dislike"


@app.task(name="tasks.clear_notif")
def clear_notif(user_id):
    print "clear notif"
    return "clear botif"


# @app.task(name="tasks.post_to_followers")
# def post_to_followers(user_id, post_id):
#     # Get the users follow owner of post
#     followers = Follow.objects.filter(following_id=user_id)\
#         .values_list('follower_id', flat=True)
#     # print followers
#     for follower_id in followers:
#         # print follower
#         try:
#             Post.add_to_user_stream(post_id=post_id, user_id=follower_id)
#         except Exception, e:
#             print str(e)
#             pass
