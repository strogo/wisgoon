from django.core.management.base import BaseCommand

from pin.models import PostMetaData
from pin.models_redis import LikesRedis


class Command(BaseCommand):
    def handle(self, *args, **options):
        loop = True
        while loop:
            q = PostMetaData.objects.filter(status=PostMetaData.FULL_IMAGE_CREATE)\
                .values_list('post_id', flat=True)[:10]
            if not q:
                loop = False
            print q
            for post_id in q:
                print "post:", post_id
                LikesRedis(post_id=post_id)

            l = [int(ll) for ll in q]
            PostMetaData.objects.filter(post_id__in=l)\
                .update(status=PostMetaData.REDIS_CHANGE_SERVER)
