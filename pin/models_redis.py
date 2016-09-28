import redis
import time
import datetime

from django.conf import settings
from django.db.models import F
from django.contrib.auth.models import User

from user_profile.models import Profile
from pin.api6.cache_layer import PostCacheLayer

from models import Post
from khayyam import JalaliDate

from pin.analytics import like_act
from pin.models_casper import PostStats, Notification

# redis set server
rSetServer = redis.Redis(settings.REDIS_DB_2, db=9)
# redis list server
rListServer = redis.Redis(settings.REDIS_DB_2, db=4)
leaderBoardServer = redis.Redis(settings.REDIS_DB_2, db=0)
activityServer = redis.Redis(settings.REDIS_DB_3)

notificationRedis = redis.Redis(settings.REDIS_DB_4)


class PostView(object):
    post_id = None
    KEY_PREFIX = "pv:1:{}"

    def __init__(self, post_id):
        self.post_id = int(post_id)
        self.KEY_PREFIX = self.KEY_PREFIX.format(post_id)

    def inc_view_test(self):
        PostStats(post_id=self.post_id).inc_view()

    def inc_view(self):
        from pin.api6.tools import is_system_writable
        if is_system_writable():
            try:
                PostStats(post_id=self.post_id).inc_view()
            except Exception, e:
                print str(e)

    def get_cnt_view(self):
        try:
            return PostStats(post_id=self.post_id).get_cnt_view()
        except:
            return 0


class NotifStruct:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class NotificationRedis(object):
    user_id = None
    KEY_PREFIX = "n:01:{}"
    KEY_PREFIX_CNT = "nc:01:{}"

    def __init__(self, user_id):
        self.user_id = int(user_id)
        self.KEY_PREFIX = self.KEY_PREFIX.format(user_id)
        self.KEY_PREFIX_CNT = self.KEY_PREFIX_CNT.format(user_id)

    def set_notif(self, ntype, post, actor, seen=False, post_image=None):
        from pin.api6.tools import is_system_writable

        if is_system_writable():
            n = Notification()
            n.set_notif(self.user_id, ntype, actor, post, int(time.time()))
            notif_str = "{}:{}:{}:{}:{}:{}"\
                .format(ntype, post, actor, seen, post_image, int(time.time()))

            np = notificationRedis.pipeline()
            np.lpush(self.KEY_PREFIX, notif_str)
            np.ltrim(self.KEY_PREFIX, 0, 1000)
            np.incr(self.KEY_PREFIX_CNT)
            np.execute()

    def get_notif(self, start=0, limit=20):
        # end = start + limit
        # nlist = notificationRedis.lrange(self.KEY_PREFIX, start, end)
        us = Notification()
        nobjesct = []
        for nl in us.get_notif(self.user_id, start):
            o = {}
            post_id = nl.object_id
            notif_type = nl.type

            if notif_type == 4:
                continue

            if not post_id:
                post_id = 0

            o['id'] = nl.date

            o['type'] = nl.type
            o['post'] = nl.object_id
            o['last_actor'] = nl.actor
            o['seen'] = True
            o['post_image'] = ""
            o['owner'] = self.user_id

            o['date'] = nl.date

            nobjesct.append(NotifStruct(**o))

        return nobjesct

    def clear_notif_count(self):
        from pin.api6.tools import is_system_writable

        if is_system_writable():
            notificationRedis.set(self.KEY_PREFIX_CNT, 0)

    def get_notif_count(self):
        cnt = notificationRedis.get(self.KEY_PREFIX_CNT)
        if not cnt:
            cnt = 0
        return cnt


class ActivityRedis(object):
    KEY_PREFIX_LIST = "act:1.0:{}"
    USER_ID = None

    LIKE = 1
    COMMENT = 2
    FOLLOW = 3

    def __init__(self, user_id):
        self.USER_ID = user_id
        self.KEY_PREFIX_LIST = self.KEY_PREFIX_LIST.format(user_id)

    def get_activity(self):
        from pin.api6.tools import post_item_json, get_simple_user_object
        act_data = activityServer.lrange(self.KEY_PREFIX_LIST, 0, 50)
        jdata = []
        for actd in act_data:
            try:
                act_type, actor, object_id = actd.split(":")
                o = {}
                o['object'] = post_item_json(int(object_id), self.USER_ID)
                o['actor'] = get_simple_user_object(int(actor))
                o['act_type'] = int(act_type)
                jdata.append(o)
            except:
                pass
        return jdata

    @classmethod
    def push_to_activity(cls, act_type, who, post_id):
        from pin.models import Follow
        flist = Follow.objects.filter(following_id=who)\
            .values_list('follower_id', flat=True)
        asp = activityServer.pipeline()
        for u in flist:
            cpl = cls.KEY_PREFIX_LIST.format(u)
            data = "{}:{}:{}".format(act_type, who, post_id)
            asp.lpush(cpl, data)
            asp.ltrim(cpl, 0, 50)
        asp.execute()


class LikesRedis(object):
    KEY_PREFIX_SET = "p:l:"
    KEY_PREFIX_LIST = "l:l:"
    KEY_LEADERBORD = "-".join(str(JalaliDate.today()).split("-")[:2])
    KEY_LEADERBORD_GROUPS = "%s-{}" % KEY_LEADERBORD

    postId = 0
    postOwner = 0
    likesData = []
    cntLike = None

    def __init__(self, post_id=None):
        if post_id:
            self.postId = int(post_id)
            self.postId = str(post_id)
            self.keyNameSet = self.KEY_PREFIX_SET + self.postId
            self.keyNameList = self.KEY_PREFIX_LIST + self.postId

    def delete_likes(self):
        rListServer.delete(self.keyNameList)
        rSetServer.delete(self.keyNameSet)

    def get_likes(self, offset, limit=20, as_user_object=False):
        smems = list(rSetServer.smembers(self.keyNameSet))
        data = smems[offset: offset + limit]

        if not as_user_object:
            return data

        ul = []
        for uid in data:
            try:
                ul.append(User.objects.only('id', 'username').get(pk=int(uid)))
            except User.DoesNotExist:
                rListServer.lrem(self.keyNameList, uid)
        return ul

    def user_liked(self, user_id):
        if rSetServer.sismember(self.keyNameSet, str(user_id)):
            return True
        return False

    def cntlike(self):
        if self.cntLike:
            return self.cntLike
        self.cntLike = rSetServer.scard(self.keyNameSet)
        return self.cntLike

    def dislike(self, user_id, post_owner):
        rListServer.lrem(self.keyNameList, user_id)
        rSetServer.srem(self.keyNameSet, str(user_id))
        Post.objects.filter(pk=int(self.postId))\
            .update(cnt_like=F('cnt_like') - 1)

        user_last_likes = "{}_{}".\
            format(settings.USER_LAST_LIKES, int(user_id))
        rListServer.lrem(user_last_likes, self.postId)

        Profile.after_dislike(user_id=post_owner)

        from pin.model_mongo import MonthlyStats
        MonthlyStats.log_hit(object_type=MonthlyStats.DISLIKE)

    def like(self, user_id, post_owner, user_ip):
        rSetServer.sadd(self.keyNameSet, str(user_id))

        p = rListServer.pipeline()
        user_last_likes = "{}_{}".\
            format(settings.USER_LAST_LIKES, int(user_id))
        p.lrem(user_last_likes, self.postId)
        p.lpush(user_last_likes, self.postId)
        p.ltrim(user_last_likes, 0, 1000)
        p.execute()

        Post.objects.filter(pk=int(self.postId))\
            .update(cnt_like=F('cnt_like') + 1)

        Profile.after_like(user_id=post_owner)

        from pin.model_mongo import MonthlyStats
        MonthlyStats.log_hit(object_type=MonthlyStats.LIKE)

        like_act(post=self.postId, actor=user_id, user_ip=user_ip)

        if user_id != post_owner:
            from pin.actions import send_notif_bar
            send_notif_bar(user=post_owner,
                           type=settings.NOTIFICATION_TYPE_LIKE,
                           post=self.postId,
                           actor=user_id)

    def like_or_dislike(self, user_id, post_owner,
                        user_ip="127.0.0.1", category=1):
        leader_category = self.KEY_LEADERBORD_GROUPS.format(category)
        lbs = leaderBoardServer.pipeline()
        if self.user_liked(user_id=user_id):
            self.dislike(user_id=user_id, post_owner=post_owner)
            lbs.zincrby(self.KEY_LEADERBORD, post_owner, -10)
            lbs.zincrby(leader_category, post_owner, -10)
            PostCacheLayer(post_id=self.postId).like_change(self.cntlike())
            liked = False
            disliked = True

        else:
            self.like(user_id=user_id, post_owner=post_owner, user_ip=user_ip)

            # from pin.tasks import activity
            # if settings.DEBUG:
            #     activity(act_type=1, who=user_id, post_id=self.postId)
            # else:
            #     activity.delay(act_type=1, who=user_id, post_id=self.postId)

            lbs.zincrby(self.KEY_LEADERBORD, post_owner, 10)
            lbs.zincrby(leader_category, post_owner, 10)
            PostCacheLayer(post_id=self.postId).like_change(self.cntlike())
            liked = True
            disliked = False

        lbs.execute()

        return liked, disliked, self.cntlike()

    def get_leaderboards(self):
        return leaderBoardServer\
            .zrevrange(self.KEY_LEADERBORD, 0, 23, withscores=True)

    def get_leaderboards_groups(self, category):
        leader_category = self.KEY_LEADERBORD_GROUPS.format(category)
        return leaderBoardServer\
            .zrevrange(leader_category, 0, 3, withscores=True)
