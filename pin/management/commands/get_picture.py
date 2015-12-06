import urllib
from django.conf import settings
from django.core.management.base import BaseCommand
import random


class Command(BaseCommand):
    def handle(self, *args, **options):
        cnt_picture = raw_input("How many picture you want to download?")
        media_url = settings.MEDIA_ROOT
        for index in xrange(1, int(cnt_picture) + 1):
            filename = "post_%s.jpg" % str(index)
            full_path = "%s/v2/test_data/images/%s" % (media_url, filename)
            image_url = "http://lorempixel.com/500/%s/" % (random.randint(300, 800))

            testfile = urllib.URLopener()
            testfile.retrieve(image_url, full_path)
            print "Download %s picture" % str(index)
