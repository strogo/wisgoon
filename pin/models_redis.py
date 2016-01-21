import redis
from django.conf import settings
from django.db.models import F
from django.contrib.auth.models import User

from user_profile.models import Profile
from pin.api6.cache_layer import PostCacheLayer

from models import Post
from khayyam import JalaliDate

from pin.analytics import like_act

# redis set server
rSetServer = redis.Redis(settings.REDIS_DB_2, db=9)
# redis list server
rListServer = redis.Redis(settings.REDIS_DB_2, db=4)
leaderBoardServer = redis.Redis(settings.REDIS_DB_2, db=0)
activityServer = redis.Redis(settings.REDIS_DB_3)


class ActivityRedis(object):
    KEY_PREFIX_LIST = "act:1.0:{}"

    LIKE = 1
    COMMENT = 2
    FOLLOW = 3

    def __init__(self, user_id):
        self.KEY_PREFIX_LIST = self.KEY_PREFIX_LIST.format(user_id)

    def get_activity(self):
        from pin.api6.tools import post_item_json, get_simple_user_object
        act_data = activityServer.lrange(self.KEY_PREFIX_LIST, 0, -1)
        jdata = []
        for actd in act_data:
            act_type, actor, object_id = actd.split(":")
            o = {}
            o['object'] = post_item_json(int(object_id))
            o['actor'] = get_simple_user_object(int(actor))
            o['act_type'] = int(act_type)
            jdata.append(o)
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

    postId = 0
    postOwner = 0
    likesData = []
    cntLike = None

    def __init__(self, post_id=None):
        if post_id:
            self.postId = str(post_id)
            self.keyNameSet = self.KEY_PREFIX_SET + self.postId
            self.keyNameList = self.KEY_PREFIX_LIST + self.postId

    def delete_likes(self):
        rListServer.delete(self.keyNameList)
        rSetServer.delete(self.keyNameSet)

    def get_likes(self, offset, limit=20, as_user_object=False):
        data = rListServer.lrange(self.keyNameList, offset, offset + limit - 1)
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
        self.cntLike = rListServer.llen(self.keyNameList)
        return self.cntLike

    def dislike(self, user_id):
        rListServer.lrem(self.keyNameList, user_id)
        rSetServer.srem(self.keyNameSet, str(user_id))
        Post.objects.filter(pk=int(self.postId))\
            .update(cnt_like=F('cnt_like') - 1)

        user_last_likes = "{}_{}".\
            format(settings.USER_LAST_LIKES, int(user_id))
        rListServer.lrem(user_last_likes, self.postId)

        Profile.after_dislike(user_id=user_id)

        from pin.model_mongo import MonthlyStats
        MonthlyStats.log_hit(object_type=MonthlyStats.DISLIKE)

    def like(self, user_id, post_owner):
        rSetServer.sadd(self.keyNameSet, str(user_id))

        Post.objects.filter(pk=int(self.postId))\
            .update(cnt_like=F('cnt_like') + 1)

        p = rListServer.pipeline()
        p.lpush(self.keyNameList, user_id)
        # Store user_last_likes
        user_last_likes = "{}_{}".\
            format(settings.USER_LAST_LIKES, int(user_id))
        p.lrem(user_last_likes, self.postId)
        p.lpush(user_last_likes, self.postId)
        p.ltrim(user_last_likes, 0, 1000)
        p.execute()

        Profile.after_like(user_id=post_owner)

        from pin.model_mongo import MonthlyStats
        MonthlyStats.log_hit(object_type=MonthlyStats.LIKE)
        like_act(post=self.postId, actor=user_id)

        if user_id != post_owner:
            from pin.actions import send_notif_bar
            send_notif_bar(user=post_owner, type=1, post=self.postId,
                           actor=user_id)

    def like_or_dislike(self, user_id, post_owner):
        if self.user_liked(user_id=user_id):
            self.dislike(user_id=user_id)
            leaderBoardServer.zincrby(self.KEY_LEADERBORD, post_owner, -10)
            PostCacheLayer(post_id=self.postId).like_change(self.cntlike())
            return False, True, self.cntlike()
        else:
            # if int(user_id) == 1:
            from pin.tasks import activity
            activity.delay(act_type=1, who=user_id, post_id=self.postId)
            self.like(user_id=user_id, post_owner=post_owner)
            leaderBoardServer.zincrby(self.KEY_LEADERBORD, post_owner, 10)
            PostCacheLayer(post_id=self.postId).like_change(self.cntlike())
            return True, False, self.cntlike()

    def get_leaderboards(self):
        return leaderBoardServer.zrevrange(self.KEY_LEADERBORD, 0, 23, withscores=True)
