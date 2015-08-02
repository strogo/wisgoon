import redis

from django.conf import settings
from django.core.management.base import BaseCommand

from pin.search_indexes import PostIndex
from pin.models import Post


class Command(BaseCommand):
    def handle(self, *args, **options):
        r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)
        s = r_server.smembers("ChangedPostsV1")

        for cp in s:
            try:
                pi = PostIndex()
                pi.update_object(Post.objects.get(id=cp))
                r_server.srem("ChangedPostsV1", cp)
            except Exception, e:
                print str(e)
