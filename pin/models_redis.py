import redis
import time
from django.conf import settings
from django.db.models import F
from django.contrib.auth.models import User

from user_profile.models import Profile
from models import Post, Likes

# r_server = redis.Redis(settings.REDIS_DB, db=12)
r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)
r_server2 = redis.Redis(settings.REDIS_DB_2, db=settings.REDIS_DB_NUMBER_2)


class ChangedPosts(object):
    KEY_PREFIX = "ChangedPostsV1"

    @classmethod
    def store_change(cls, post_id):
        r_server.sadd(cls.KEY_PREFIX, post_id)

    @classmethod
    def get_changed(cls):
        s = r_server.smembers(cls.KEY_PREFIX)
        l = [i for i in s][:20]
        print l
        if l:
            r_server.srem(cls.KEY_PREFIX, *l)
        return l


class LikesRedis(object):
    KEY_PREFIX = "postLikersV1"
    KEY_PREFIX2 = "p:l:"
    keyName = ""
    postId = 0
    postOwner = 0
    likesData = []

    def __init__(self, post_id):
        self.postId = str(post_id)
        self.keyName = self.KEY_PREFIX + self.postId
        self.keyName2 = self.KEY_PREFIX2 + self.postId

        if not r_server2.exists(self.keyName2):
            # r_server.zadd(self.keyName2)
            keys = r_server.lrange(self.keyName, 0, -1)
            p = r_server2.pipeline()
            for uid in keys[::-1]:
                p.zadd(self.keyName2, str(uid), time.time())
            p.execute()

    def get_likes(self, offset, limit=20, as_user_object=False):
        data = r_server.lrange(self.keyName, offset, offset + limit - 1)
        if not as_user_object:
            return data

        ul = []
        for uid in data:
            try:
                ul.append(User.objects.only('id', 'username').get(pk=int(uid)))
            except User.DoesNotExist:
                r_server.lrem(self.keyName, uid)
        return ul

    def first_store(self):
        likes = Likes.objects.values_list('user_id', flat=True)\
            .filter(post_id=self.postId).order_by('-id')
        if likes:
            # likes = [-1]
            r_server.rpush(self.keyName, *likes)

    def user_liked(self, user_id):
        if r_server2.zrank(self.keyName2, str(user_id)) is None:
            return False
        return True

        self.likesData = r_server.lrange(self.keyName, 0, -1)
        if str(user_id) in self.likesData:
            return True
        return False

    def cntlike(self):
        return r_server.llen(self.keyName)

    def dislike(self, user_id):
        r_server.lrem(self.keyName, user_id)
        r_server2.zrem(self.keyName2, str(user_id))
        Post.objects.filter(pk=int(self.postId))\
            .update(cnt_like=F('cnt_like') - 1)

        user_last_likes = "%s_%d" % (settings.USER_LAST_LIKES, int(user_id))
        r_server.lrem(user_last_likes, self.postId)

        Profile.after_dislike(user_id=user_id)

    def store_last_likes(self):
        # Stroe last likes
        r_server.lrem(settings.LAST_LIKES, self.postId)
        r_server.lpush(settings.LAST_LIKES, self.postId)
        r_server.ltrim(settings.LAST_LIKES, 0, 1000)

    def like(self, user_id, post_owner):
        r_server2.zadd(self.keyName2, str(user_id), time.time())
        r_server.lpush(self.keyName, user_id)
        Post.objects.filter(pk=int(self.postId))\
            .update(cnt_like=F('cnt_like') + 1)

        ChangedPosts.store_change(post_id=self.postId)

        self.store_last_likes()

        # Store user_last_likes
        user_last_likes = "%s_%d" % (settings.USER_LAST_LIKES, int(user_id))
        r_server.lrem(user_last_likes, self.postId)
        r_server.lpush(user_last_likes, self.postId)
        r_server.ltrim(user_last_likes, 0, 1000)

        Profile.after_like(user_id=post_owner)

        # Post.hot(post.id, amount=0.5)
        from pin.tasks import send_notif_bar

        send_notif_bar(user=post_owner, type=1, post=self.postId,
                       actor=user_id)

    def like_or_dislike(self, user_id, post_owner):
        if self.user_liked(user_id=user_id):
            # print "user liked"
            self.dislike(user_id=user_id)
            return False, True, self.cntlike()
        else:
            self.like(user_id=user_id, post_owner=post_owner)
            return True, False, self.cntlike()
