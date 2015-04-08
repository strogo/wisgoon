from django.core.management.base import BaseCommand

from pin.models import Likes
from pin.models_redis import LikesRedis


class Command(BaseCommand):
    def handle(self, *args, **options):
        for l in Likes.objects.values_list('post_id', flat=True).distinct()[:10000]:
            print l
            LikesRedis(post_id=l)
