import urllib
import time
from django.core.management.base import BaseCommand
from django.conf import settings

from instagram import client
from pin.models import Post
from pin.model_mongo import InstaMeta
from pin.tools import create_filename

MEDIA_ROOT = settings.MEDIA_ROOT


def get_from_insta():
    client_id = "ecb7cbd35a11467fb2cf558583a44047"
    client_secret = "74e85dfb6b904ac68139a93a9b047247"
    api = client.InstagramAPI(client_id=client_id, client_secret=client_secret)

    recent_media, next_ = api.user_recent_media(user_id="1462129775", count=5)

    for media in recent_media:
        if media.type == "image":
            id = media.id
            if InstaMeta.objects(insta_id=id).count() != 0:
                continue

            model = Post()
            model.text = media.caption.text
            model.image = media.get_standard_resolution_url()

            image_url = model.image
            filename = image_url.split('/')[-1]
            filename = create_filename(filename)
            image_on = "%s/pin/images/o/%s" % (MEDIA_ROOT, filename)

            urllib.urlretrieve(image_url, image_on)

            model.image = "pin/images/o/%s" % (filename)
            model.timestamp = time.time()
            model.user_id = 636690
            model.status = Post.APPROVED
            model.save()

            InstaMeta.objects.create(post=model.id, insta_id=id)


class Command(BaseCommand):
    def handle(self, *args, **options):
        get_from_insta()
