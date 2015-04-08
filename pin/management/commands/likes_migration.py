from django.core.management.base import BaseCommand

from pin.models import Likes
from pin.models_redis import LikesRedis


class Command(BaseCommand):
    def handle(self, *args, **options):
        for l in Likes.objects.only('post').all()[:10000]:
            print l.post_id
            LikesRedis(post_id=l.post_id)
