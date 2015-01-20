import datetime
from mongoengine import *
from django.conf import settings

connect(settings.MONGO_DB)

class Comment(EmbeddedDocument):
    content = StringField()
    name = StringField(max_length=120)


class BlogPost(Document):
    title = StringField()
    text = StringField()
    likers = ListField(IntField())
    tags = ListField(StringField())
    create_time = DateTimeField()
    comments = ListField(EmbeddedDocumentField(Comment))

    meta = {
        'indexes':['tags']
    }

