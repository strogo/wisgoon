import os
from urlparse import urlparse
import hashlib
import urllib

import tldextract

from django.core.management.base import BaseCommand
from django.conf import settings

from rss.models import Feed
from rss.utils import get_host

def get_favicon_url(url):
    o = urlparse(url)
    host = get_host(url)
    print "get favicon: ", host
    favloc = "%s/favicon/%s.ico" % ( settings.MEDIA_ROOT, host )
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
