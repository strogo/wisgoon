from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from pin.models_casper import UserStream
from pin.models import Post, Follow


class Command(BaseCommand):
    def handle(self, *args, **options):
        users = User.objects.only('id').all()
        us = UserStream()
        for user in users:
            print "user:", user.id
            q = Follow.objects.filter(follower_id=user.id)
            for f in q:
                pid_list = Post.objects.filter(user_id=f.following_id)\
                    .only("id")\
                    .values_list("id", flat=True)\
                    .order_by("-id")[:100]
                us.follow(user.id, pid_list, f.following_id)
            us.ltrim(user.id, 10)
