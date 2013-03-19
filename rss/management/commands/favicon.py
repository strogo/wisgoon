import os
from urlparse import urlparse
import hashlib
import urllib

from django.core.management.base import BaseCommand
from django.conf import settings

from rss.models import Feed

def get_favicon_url(url):
    o = urlparse(url)
    favloc = "%s/favicon/%s.ico" % ( settings.MEDIA_ROOT, hashlib.md5(o.netloc).hexdigest() )
    #print "fav location: ", favloc
    favurl = "http://g.etfv.co/%s://%s" % (o.scheme ,o.netloc)
    urllib.urlretrieve(favurl, favloc)

class Command(BaseCommand):
    def handle(self, *args, **options):

        if not os.path.exists("%s/favicon" % ( settings.MEDIA_ROOT )):
            os.makedirs("%s/favicon" % ( settings.MEDIA_ROOT ))

        feeds  = Feed.objects.all()
        for feed in feeds:
            get_favicon_url( feed.url)
