from mongoengine import *

connect('wisgoon')

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
