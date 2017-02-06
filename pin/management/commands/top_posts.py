from django.core.management.base import BaseCommand
import redis

from pin.models import Post
from django.conf import settings

ss = redis.Redis(settings.REDIS_DB_104)


class Command(BaseCommand):
    def handle(self, *args, **options):
        status = True
        limit = 100
        offset = 0

        while status:
            posts = Post.objects.only('id', 'cnt_like')\
                .order_by('-cnt_like')[offset:offset + limit]
            print "offset: {}".format(offset)
            offset = offset + limit
            if offset > 1000:
                status = False
            for post in posts:
                ss.zadd('top_all', post.id, post.cnt_like)
