from django.core.management.base import BaseCommand

from pin.models_redis import LikesRedis


class Command(BaseCommand):
    def handle(self, *args, **options):
        # LikesRedis(post_id=60).user_liked(1)
        # LikesRedis(post_id=60).user_liked(7)
        # LikesRedis(post_id=60).user_liked(8)

        print LikesRedis(post_id=60).like_or_dislike(user_id=1)
