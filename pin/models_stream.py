import redis
from django.conf import settings
from pin.models_casper import UserStream

# stream server 
ss = redis.Redis(settings.REDIS_DB_104)

# user stream production
stream_key = "usp002:{}"

stream_limit = 500

class RedisUserStream(object):
	def __init__(self):
		pass

	def migrate_user_stream(self, user_id):
		skey = stream_key.format(user_id)
		if not ss.exists(skey):
			us = UserStream()
			uslist = []
			for r in us.get_post_data(user_id, 0, stream_limit):
				post_hash = "{}:{}".format(r.post_id, r.post_owner)
				uslist.append(post_hash)

			uslist.reverse()
			for ul in uslist:
				ss.lpush(skey, ul)

	def add_post(self, user_ids, post_id, post_owner):
		post_hash = "{}:{}".format(post_id, post_owner)
		for uid in user_ids:
			skey = stream_key.format(uid)
			self.migrate_user_stream(uid)
			ss.lpush(skey, post_hash)
			ss.ltrim(skey, 0, stream_limit - 1)


	def get_posts(self, user_id):
		self.migrate_user_stream(user_id)

	