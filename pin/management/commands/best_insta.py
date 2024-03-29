import socket
import requests
import time
import shutil

from datetime import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

from instagram import client
from pin.models import Post, InstaAccount
from pin.model_mongo import InstaMeta
from pin.tools import create_filename

MEDIA_ROOT = settings.MEDIA_ROOT

socket.setdefaulttimeout(30)


def get_from_insta(insta_user_id, cat, user_id, cnt=5):
    client_id = "ecb7cbd35a11467fb2cf558583a44047"
    client_secret = "74e85dfb6b904ac68139a93a9b047247"
    api = client.InstagramAPI(client_id=client_id, client_secret=client_secret)

    recent_media, next_ = api.user_recent_media(user_id=insta_user_id,
                                                count=cnt)

    for media in recent_media:
        if media.type == "image":
            try:
                id = media.id
                if InstaMeta.objects(insta_id=id).count() != 0:
                    continue

                print "store:", id

                model = Post()
                model.text = media.caption.text
                model.image = media.get_standard_resolution_url()

                image_url = model.image
                # filename = image_url.split('/')[-1]
                filename = create_filename('1.jpg')
                image_on = "%s/pin/%s/images/o/%s" % (MEDIA_ROOT, settings.INSTANCE_NAME, filename)

                # image_url = image_url.replace("https://", "http://")
                print image_url

                response = requests.get(image_url, stream=True)
                print response.status_code
                if response.status_code != 200:
                    continue

                with open(image_on, 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response

                # urllib.urlretrieve(image_url, image_on)

                model.image = "pin/%s/images/o/%s" % (settings.INSTANCE_NAME, filename)
                model.timestamp = time.time()
                model.user_id = user_id
                model.status = Post.APPROVED
                model.category_id = cat
                model.save()

                InstaMeta.objects.create(post=model.id, insta_id=id)
            except Exception, e:
                print str(e)


class Command(BaseCommand):
    def handle(self, *args, **options):
        for ac in InstaAccount.objects.order_by('lc'):
            print "going to get", ac.insta_id
            try:
                get_from_insta(str(ac.insta_id), ac.cat_id, ac.user_id)
            except Exception, e:
                print str(e)
            ac.lc = datetime.now()
            ac.save()
        # get_from_insta(insta_user_id="1462129775", cat=7, user_id=636690)
        # get_from_insta(insta_user_id="1222617046", cat=16, user_id=636690)
        # get_from_insta(insta_user_id="306728731", cat=17, user_id=636690)
        # get_from_insta(insta_user_id="333554794", cat=17, user_id=636690)
        # get_from_insta(insta_user_id="693947917", cat=13, user_id=636690)
        # get_from_insta(insta_user_id="1683733211", cat=20, user_id=636690)
        # get_from_insta(insta_user_id="1588368877", cat=4, user_id=636690)
        # get_from_insta(insta_user_id="2772314", cat=17, user_id=636690)
        # get_from_insta(insta_user_id="42059454", cat=1, user_id=636690)
        # get_from_insta(insta_user_id="675083963", cat=16, user_id=636690)
        # get_from_insta(insta_user_id="1072975326", cat=17, user_id=636690)
        # get_from_insta(insta_user_id="28584235", cat=39, user_id=636690)
        # get_from_insta(insta_user_id="1119171968", cat=39, user_id=636690)

        # get_from_insta(insta_user_id="197997900", cat=3, user_id=636878)
