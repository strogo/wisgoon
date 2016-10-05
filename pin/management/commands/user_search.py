# import redis

from django.core.management.base import BaseCommand
# from django.conf import settings
from django.contrib.auth.models import User

# from pin.models import Post
# from pin.models_casper import UserStream
from pin.models_es import ESUsers

from user_profile.models import Profile
# from pin.api6.tools import post_item_json

# r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects\
            .only('username', 'email', 'id').all()
        us = ESUsers()
        for user in users:
            try:
                q = Profile.objects.only('name', 'bio',
                                         'is_private', 'cnt_followers')\
                    .get(user_id=user.id)
            except Profile.DoesNotExist:
                continue
            user.profile_object = q
            print "index", user.id
            us.save(user)
