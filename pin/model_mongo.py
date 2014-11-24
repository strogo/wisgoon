from mongoengine import *
from django.conf import settings

connect(settings.MONGO_DB)


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
