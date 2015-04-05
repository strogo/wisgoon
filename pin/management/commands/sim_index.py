from django.core.management.base import BaseCommand
from django.conf import settings
from pin.models import Post, Sim
from pyimagesearch.colordescriptor import ColorDescriptor
import cv2


class Command(BaseCommand):
    def handle(self, *args, **options):
        for p in Post.objects.all()[:1000]:
            im = p.get_image_500(api=True)
            if not im:
                continue

            cd = ColorDescriptor((8, 12, 3))

            image_path = settings.MEDIA_ROOT + "/" + im['url']
            print image_path
            image = cv2.imread(image_path)

            # describe the image
            features = cd.describe(image)

            # write the features to file
            features = [str(f) for f in features]
            Sim.objects.get_or_create(post_id=p.id, features=",".join(features))
