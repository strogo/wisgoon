import redis

from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from pin.models_casper import UserStream
from pin.api6.tools import post_item_json

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.only('id').all()
        us = UserStream()
        for user in users:
            print "user:", user.id
            user_stream = "{}_{}".format(settings.USER_STREAM, int(user.id))
            pl = r_server.lrange(user_stream, 0, 1000)
            if not pl:
                continue

            for pll in pl:
                pll_id = int(pll)
                ob = post_item_json(pll_id)
                if not ob:
                    continue
                us.add_post(user.id, pll_id, ob['user']['id'])

            us.ltrim(user.id, 1000)
