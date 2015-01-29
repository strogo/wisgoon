# -*- coding: utf-8
import datetime
import redis
from mongoengine import *
from mongoengine import signals
from django.conf import settings

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)

connect(settings.MONGO_DB)

class FixedAds(Document):
    post = IntField()
    cnt_view = IntField(default=0)
    ttl = IntField(default=86400)

class Ads(Document):
    TYPE_1000_USER = 1
    TYPE_3000_USER = 2
    TYPE_6000_USER = 3
    TYPE_15000_USER = 4


    MAX_TYPES = {
        TYPE_1000_USER: 1000,
        TYPE_3000_USER: 3000,
        TYPE_6000_USER: 6000,
        TYPE_15000_USER: 15000,
    }

    TYPE_PRICES = {
        TYPE_1000_USER: 500,
        TYPE_3000_USER: 1000,
        TYPE_6000_USER: 2000,
        TYPE_15000_USER: 5000,
    }

    user = IntField()
    approved = BooleanField(default=True)
    ended = BooleanField(default=False)
    cnt_view = IntField(default=0)
    post = IntField()
    ads_type = IntField(default=TYPE_1000_USER)
    users = ListField(StringField())
    start = DateTimeField()
    end = DateTimeField()

    meta ={
        'indexes': ['users', ('ads_type', 'users'), ('users', 'ended')]
    }

    @classmethod
    def get_ad(self, user_id):
        # print "viewer id:", user_id
        try:
            ad = Ads.objects.filter(users__nin=[user_id], ended=False)[:1]
            if ad:
                ad = ad[0]
                if ad.cnt_view >= self.MAX_TYPES[ad.ads_type]:
                    Ads.objects(pk=ad.id).update(add_to_set__users=user_id,
                                                 inc__cnt_view=1,
                                                 set__end=datetime.datetime.now(),
                                                 set__ended=True)
                else:
                    # pass
                    Ads.objects(pk=ad.id).update(add_to_set__users=user_id, inc__cnt_view=1)
                return ad
        except Exception, e:
            print str(e), "models_mongo 50"
        return None



class Bills(Document):
    user = IntField()
    status = IntField(default=0)
    amount = IntField()
    trans_id = StringField()

    meta = {
        'indexes': ['user']
    }


class PostMeta(Document):
    post = IntField()
    img_236 = StringField()
    img_236_h = IntField()

    img_500 = StringField()
    img_500_h = IntField()

    meta = {
        'indexes': ['post']
    }


class PendingPosts(Document):
    user = IntField()
    post = IntField()

    meta = {
        'indexes': ['post']
    }

    @classmethod
    def is_pending(self, post):
        post = int(post)
        if r_server.sismember(settings.PENDINGS, post):
            print "this post is pending"
            return True
        print "this post is not pending"
        return False

    def save(self, *args, **kwargs):
        from models import Post
        p = Post.objects.only('category').get(id=int(self.post))
        r_server.lrem(settings.STREAM_LATEST, str(self.post))

        cat_stream = "%s_%s" % (settings.STREAM_LATEST, p.category.id)
        r_server.lrem(cat_stream, str(self.post))

        print "save in pending"
        r_server.sadd(settings.PENDINGS, int(self.post))
        return super(PendingPosts, self).save(*args, **kwargs)

    def delete(self, **write_concern):
        from models import Post
        p = Post.objects.only('category').get(id=int(self.post))
        r_server.lpush(settings.STREAM_LATEST, str(self.post))

        # cat_stream = "%s_%s" % (settings.STREAM_LATEST, p.category.id)
        # r_server.lpush(cat_stream, str(self.post))

        cat_stream = "%s_%s" % (settings.STREAM_LATEST_CAT, p.category.id)
        r_server.lrem(cat_stream, p.id)
        r_server.lpush(cat_stream, p.id)

        print "delete in pending"
        r_server.srem(settings.PENDINGS, int(self.post))
        return super(PendingPosts, self).delete(**write_concern)


def unpending(sender, document):
    print "unpending"

signals.post_delete.connect(unpending)


class UserMeta(Document):
    insta_token = StringField()
    insta_id = IntField()
    user = IntField()

    credit = IntField(default=0)
    level = IntField(default=1)

    meta = {
        'indexes': ['user', '-credit']
    }

    def get_level_string(self):
        if self.level == 1:
            return u'عادی'
        elif self.level == 2:
            return u'پلیس'

    def is_police(self):
        if self.level == 2:
            return True
        return False


class Notif(Document):
    last_actor = IntField()
    date = DateTimeField()
    post = IntField()
    owner = IntField()
    actors = ListField()
    type = IntField()
    seen = BooleanField(default=False)

    meta = {
        'indexes': ['owner', 'post', ('owner', '-date'), ('owner', 'type', 'post'), ('seen', 'owner')]
    }

    def last_actors(self, num=12):
        la = self.actors[::-1][:num]
        return la


class MonthlyStats(Document):

    POST = "post"
    COMMENT = "comment"
    LIKE = "like"

    date = DateTimeField()
    object_type = StringField()
    count = IntField()

    meta = {
        'indexes': ['date', ('object_type', 'date')]
    }

    @classmethod
    def log_hit(self, object_type):
        d = str(datetime.date.today())
        MonthlyStats.objects(date=d, object_type=object_type)\
            .update_one(inc__count=1, upsert=True)
