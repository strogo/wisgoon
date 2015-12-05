import urllib
from django.conf import settings
from django.core.management.base import BaseCommand
import random


class Command(BaseCommand):
    def handle(self, *args, **options):
        media_url = settings.MEDIA_ROOT
        for index in xrange(1, 51):
            filename = "post_%s.jpg" % str(index)
            full_path = "%s/pin/blackhole/test_data/%s" % (media_url, filename)
            image_url = "http://lorempixel.com/500/%s/" % (random.randint(300, 800))

            testfile = urllib.URLopener()
            testfile.retrieve(image_url, full_path)
            print "Download %s picture" % str(index)
