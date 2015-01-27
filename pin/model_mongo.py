import datetime
from mongoengine import *
from django.conf import settings

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


class UserMeta(Document):
    insta_token = StringField()
    insta_id = IntField()
    user = IntField()

    credit = IntField(default=0)

    meta = {
        'indexes': ['user', '-credit']
    }


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
