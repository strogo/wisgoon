import redis
from django.conf import settings
from django.db.models import F
from django.contrib.auth.models import User

from user_profile.models import Profile
from models import Post

# redis set server
rSetServer = redis.Redis(settings.REDIS_DB_2, db=9)
# redis list server
rListServer = redis.Redis(settings.REDIS_DB_2, db=4)


class LikesRedis(object):
    KEY_PREFIX_SET = "p:l:"
    KEY_PREFIX_LIST = "l:l:"

    postId = 0
    postOwner = 0
    likesData = []

    def __init__(self, post_id):
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
        return rListServer.llen(self.keyNameList)

    def dislike(self, user_id):
        rListServer.lrem(self.keyNameList, user_id)
        rSetServer.srem(self.keyNameSet, str(user_id))
        Post.objects.filter(pk=int(self.postId))\
            .update(cnt_like=F('cnt_like') - 1)

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
        user_last_likes = "%s_%d" % (settings.USER_LAST_LIKES, int(user_id))
        p.lrem(user_last_likes, self.postId)
        p.lpush(user_last_likes, self.postId)
        p.ltrim(user_last_likes, 0, 1000)
        p.execute()

        Profile.after_like(user_id=post_owner)

        from pin.model_mongo import MonthlyStats
        MonthlyStats.log_hit(object_type=MonthlyStats.LIKE)

        if user_id != post_owner:
            from pin.actions import send_notif_bar
            send_notif_bar(user=post_owner, type=1, post=self.postId,
                           actor=user_id)

    def like_or_dislike(self, user_id, post_owner):
        if self.user_liked(user_id=user_id):
            self.dislike(user_id=user_id)
            return False, True, self.cntlike()
        else:
            self.like(user_id=user_id, post_owner=post_owner)
            return True, False, self.cntlike()
