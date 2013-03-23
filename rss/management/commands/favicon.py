import os
from urlparse import urlparse
import hashlib
import urllib

import tldextract

from django.core.management.base import BaseCommand
from django.conf import settings

from rss.models import Feed
from rss.utils import get_host

all_check = []

def get_favicon_url(url):
    o = urlparse(url)
    host, tld = get_host(url)
    sub_suf = host+"."+tld
    file_name = host+"_"+tld
    if sub_suf not in all_check:
        print "get favicon: ", host
        favloc = "%s/favicon/%s.ico" % ( settings.MEDIA_ROOT, file_name )
        #print "fav location: ", favloc
        favurl = "http://g.etfv.co/%s://www.%s" % (o.scheme, sub_suf)
        print "favurl is: ", favurl
        urllib.urlretrieve(favurl, favloc)
        all_check.append(sub_suf)

    print "multiple in: ", sub_suf

class Command(BaseCommand):
    def handle(self, *args, **options):

        if not os.path.exists("%s/favicon" % ( settings.MEDIA_ROOT )):
            os.makedirs("%s/favicon" % ( settings.MEDIA_ROOT ))

        feeds  = Feed.objects.all()
        
        for feed in feeds:
            get_favicon_url( feed.url)
