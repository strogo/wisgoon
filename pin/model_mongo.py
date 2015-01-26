import datetime
from mongoengine import *
from django.conf import settings

connect(settings.MONGO_DB)

class Ads(Document):
    TYPE_2000_USER = 1

    user = IntField()
    approved = BooleanField(default=True)
    ended = BooleanField(default=False)
    cnt_view = IntField(default=0)
    post = IntField()
    ads_type = IntField(default=TYPE_2000_USER)
    users = ListField(StringField())

    meta ={
        'indexes': ['users', ('ads_type', 'users'), ('users', 'ended')]
    }

    @classmethod
    def get_ad(self, user_id):
        # print "viewer id:", user_id
        ad = Ads.objects.filter(users__nin=[user_id], ended=False)[:1]
        if ad:
            ad = ad[0]
            if ad.ads_type == self.TYPE_2000_USER and ad.cnt_view == 2000:
                Ads.objects(pk=ad.id).update(add_to_set__users=user_id, inc__cnt_view=1, ended=True)
            else:
                Ads.objects(pk=ad.id).update(add_to_set__users=user_id, inc__cnt_view=1)
            return ad
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
