import datetime
from mongoengine import *
from django.conf import settings

connect(settings.MONGO_DB)

class Post(Documnt):
	title = StringField()
	text = StringField()
	likers = ListField(IntegerField())
	tags = ListField(StringField())
	create_time = DateTimeField()
	
