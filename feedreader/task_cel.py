from datetime import datetime

from django.db.models import F

from pin.model_mongo import MonthlyStats
from pin.models_redis import NotificationRedis
from pin.models import Post, Follow

from user_profile.models import Profile
# from pin.my_notif import NotifCas


def notif_send(user_id, type, post, actor_id, seen=False, post_image=None):
    # NotifCount.objects(owner=user_id).update_one(inc__unread=1, upsert=True)

    # Notif.objects.create(owner=user_id, type=type, post=post,
    #                      last_actor=actor_id,
    #                      date=datetime.now,
    #                      post_image=post_image)

    NotificationRedis(user_id=user_id)\
        .set_notif(ntype=type, post=post, actor=actor_id)

    return "hello notif"


def inc_prof(user_id):
    print "inc_prof", user_id


def profile_after_like(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') + 1, score=F('score') + 10)

    MonthlyStats.log_hit(object_type=MonthlyStats.LIKE)

    return "after like"


def profile_after_dislike(user_id):
    Profile.objects.filter(user_id=user_id)\
        .update(cnt_like=F('cnt_like') - 1, score=F('score') - 10)

    return "after dislike"


def clear_notif(user_id):
    # Notif.objects.filter(owner=user_id).order_by('-date')[100:].delete()
    print "clear notif"
    return "clear botif"


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
