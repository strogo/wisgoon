from django.core.management.base import BaseCommand

from pin.models import PostMetaData


class Command(BaseCommand):
    def handle(self, *args, **options):
        q = PostMetaData.objects.only('img_236_h', 'img_500_h', 'post')\
            .filter(status=PostMetaData.CREATED)[:30]
        for pm in q:
            if pm.img_236_h == 0:
                pm.post.get_image_236()

            if pm.img_500_h == 0:
                pm.post.get_image_500()

            PostMetaData.objects.filter(pk=pm.id)\
                .update(status=PostMetaData.FULL_IMAGE_CREATE)
