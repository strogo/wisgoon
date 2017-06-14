import redis

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from pin.models_stream import RedisUserStream
# from pin.models import Post
# from pin.models_casper import UserStream

# from pin.api6.tools import post_item_json

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.filter(id__gt=1).only('id').all()
        # us = UserStream()
        us = RedisUserStream()
        for user in users:
            us.migrate_user_stream(user.id)
            print "user:", user.id
            # user_stream = "{}_{}".format(settings.USER_STREAM, int(user.id))
            # pl = r_server.lrange(user_stream, 0, 1000)
            # if not pl:
            #     continue

            # pl = [int(p) for p in pl]

            # q = Post.objects.filter(id__in=pl).only('user_id')
            # for pll in q:
            #     us.add_post(user.id, pll.id, pll.user_id)

            # us.ltrim(user.id, 1000)
