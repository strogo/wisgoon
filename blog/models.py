import datetime
from mongoengine import *
from django.conf import settings

connect(settings.MONGO_DB)

class Comment(EmbeddedDocument):
    content = StringField()
    create_time = DateTimeField()
    user = IntField()


class BlogPost(Document):
    title = StringField()
    text = StringField()
    abstract = StringField()
    likers = ListField(IntField())
    tags = ListField(StringField())
    create_time = DateTimeField()
    comments = ListField(EmbeddedDocumentField(Comment))
    user = IntField()

    meta = {
        'indexes':['tags']
    }

