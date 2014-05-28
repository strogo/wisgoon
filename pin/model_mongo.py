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
