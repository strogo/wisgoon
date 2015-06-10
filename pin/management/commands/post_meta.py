import os

from django.core.management.base import BaseCommand
from django.conf import settings

from pin.models import PostMetaData

m_root = settings.MEDIA_ROOT


class Command(BaseCommand):
    def handle(self, *args, **options):
        q = PostMetaData.objects.only('img_236_h', 'img_500_h', 'post')\
            .filter(status=PostMetaData.CREATED)[:30]
        for pm in q:
            s = os.path.join(m_root, pm.post.image)
            if not os.path.exists(s):
                PostMetaData.objects.filter(pk=pm.id)\
                    .update(status=PostMetaData.ERROR_IN_ORIGINAL)
                continue
            img_size = os.path.getsize(s)

            if pm.img_236_h == 0:
                print "create image 236 for ", pm.id
                pm.post.get_image_236()

            if pm.img_500_h == 0:
                print "create image 500 for", pm.id
                pm.post.get_image_500()

            PostMetaData.objects.filter(pk=pm.id)\
                .update(status=PostMetaData.FULL_IMAGE_CREATE,
                        original_size=img_size)
