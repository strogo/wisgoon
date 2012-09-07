import sys
from time import mktime
from datetime import datetime
import binascii

sys.path.append('/var/www/html/feedreader/')
sys.path.append('/var/www/html/')

from django.core.management import setup_environ 
import settings 
setup_environ(settings)
from django.db.utils import IntegrityError

import feedparser
from rss.models import Feed, Item


def parse_feed(feedObj):
    feed = feedparser.parse(feedObj.url)
    i=0
    duplicate=0
    try:
        for item in feed.entries:
            i=i+1
            #print "title: %s" % item.title
            #print "date: %s" % item.updated_parsed
            fi = Item()
            fi.title = item.title
            if hasattr(item, 'description'):
                fi.description = item.description
            fi.url = item.link
            fi.url_crc = binascii.crc32(item.link.encode('utf-8'))
            fi.date = datetime.fromtimestamp(mktime(item.updated_parsed))
            fi.timestamp = mktime(item.updated_parsed)
            fi.feed = feedObj
            
            fi.save()
    except IntegrityError:
        """
        duplicate value
        """
        if i==1 and feedObj.priority != 100:
            feedObj.priority = feedObj.priority+1
            duplicate=1
    
    if duplicate == 0:
        if feedObj.priority <= 5:
            feedObj.priority = 1
        else:
            feedObj.priority = feedObj.priority-5        
    
    feedObj.title=feed['channel']['title']
    feedObj.last_fetch = datetime.now()
    feedObj.save()
            

feedObj = Feed.objects.all()

for i in feedObj:
    parse_feed(i)
