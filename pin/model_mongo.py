import datetime
from mongoengine import *
from django.conf import settings

connect(settings.MONGO_DB)


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
