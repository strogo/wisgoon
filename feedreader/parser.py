from time import mktime, time
from datetime import datetime
import binascii
import feedparser
from rss.models import Item

from django.db.utils import IntegrityError
import _mysql_exceptions


def parse_feed(feedObj):
    print "going to parse %s" % feedObj.url
    feed = feedparser.parse(feedObj.url)
    print "end of getting url"
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
            
            if item.published_parsed != None:
                fi.date = datetime.fromtimestamp(mktime(item.updated_parsed))
                fi.timestamp = mktime(item.updated_parsed)
            else:
                fi.date = datetime.now()
                fi.timestamp = time()
                
            fi.feed = feedObj
            
            fi.save()
    except IntegrityError:
        """
        duplicate value
        """
        if i==1 and feedObj.priority != 100:
            feedObj.priority = feedObj.priority+1
            duplicate=1
    
    except _mysql_exceptions.Warning:
        print feedObj
    
    if duplicate == 0:
        if feedObj.priority <= 5:
            feedObj.priority = 1
        else:
            feedObj.priority = feedObj.priority-5        
    try:
        feedObj.title=feed['channel']['title']
    except KeyError:
        pass
    feedObj.last_fetch = datetime.now()
    feedObj.save()