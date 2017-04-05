import redis

from django.core.management.base import BaseCommand
from django.conf import settings

from pin.models import Post

r_server = redis.Redis(settings.REDIS_DB_2, db=settings.REDIS_DB_NUMBER)


class Command(BaseCommand):

    def handle(self, *args, **options):
        post_ids = Post.objects.values_list('id', flat=True)\
            .filter(show_in_default=True,
                    user__profile__is_private=False)\
            .order_by("-id")[:1000]
        add_to_home(post_ids)


def add_to_home(post_ids):
    for post_id in post_ids:
        # r_server.lrem(Post.HOME_QUEUE_NAME, post_id)
        # r_server.rpush(Post.HOME_QUEUE_NAME, post_id)
        r_server.lrem(settings.HOME_STREAM, post_id)
        r_server.rpush(settings.HOME_STREAM, post_id)

        print "{} add to choices".format(post_id)
