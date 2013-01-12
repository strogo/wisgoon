from time import mktime, time
from datetime import datetime
import binascii
import feedparser
from rss.models import Item

from django.db.utils import IntegrityError
import _mysql_exceptions

import lxml.html
from urllib2 import HTTPError
import re
import urllib2
import urllib
import os
import socket
from paste.script.util.uuid import UUID

socket.setdefaulttimeout(10)

def remove_img_tags(data):
    p = re.compile(r'<img.*?>')
    data = p.sub('', data)

    p = re.compile(r'<img.*?/>')
    data = p.sub('', data)
    
    return data

def parse_feed_web(feedObj):
    
    feedObj.lock = True
    feedObj.save()
    
    try:
        feed = feedparser.parse(feedObj.url)
    except:
        return 0
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
                if fi.description != '':
                    tree = lxml.html.fromstring(fi.description)
                    for image in tree.xpath("//img/@src"):
                        try:
                            
                            filename = image.split('/')[-1]
                            
                            fi.image = "rss/%d/%s" % (feedObj.id, filename)
                            
                            project = os.path.join(os.path.dirname(__file__),'media/rss')
                            
                            directory = "%s/%d/" % (project, feedObj.id)
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                            filename= "%s%s" % (directory, filename)
                            
                            urllib.urlretrieve(image, filename)
                            
                            break
                        except HTTPError:
                            pass
                        
                    #fi.description = remove_img_tags(lxml.html.tostring(tree, encoding='utf-8'))
                
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
    
    except _mysql_exceptions.Warning:
        pass
    
    finally:
        try:
            feedObj.title=feed['channel']['title']
        except KeyError:
            pass
        
        feedObj.last_fetch = datetime.now()
        feedObj.lock = False
        feedObj.save()
    
    if i==0:
        return 0
    else:
        return 1

def parse_feed(feedObj):
    
    feedObj.lock = True
    feedObj.save()
    
    print "going to parse %s" % feedObj.url
    feed = feedparser.parse(feedObj.url)
    print "end of getting url"
    i=0
    duplicate=0
    hasInsert = 0
    try:
        for item in feed.entries:
            i=i+1
            #print "title: %s" % item.title
            #print "date: %s" % item.updated_parsed
            fi = Item()
            fi.title = item.title
            if hasattr(item, 'description'):
                fi.description = item.description
                if fi.description != '':
                    tree = lxml.html.fromstring(fi.description)
                    for image in tree.xpath("//img/@src"):
                        try:
                            
                            filename = image.split('/')[-1]
                            
                            fi.image = "rss/%d/%s" % (feedObj.id, filename)
                            
                            project = os.path.join(os.path.dirname(__file__),'media/rss')
                            
                            directory = "%s/%d/" % (project, feedObj.id)
                            if not os.path.exists(directory):
                                os.makedirs(directory)
                            filename= "%s%s" % (directory, filename)
                            
                            print "Storing %s in %s" %(image, filename) 
                            urllib.urlretrieve(image, filename)
                            
                            break
                        except HTTPError:
                            pass
                        
                    #fi.description = remove_img_tags(lxml.html.tostring(tree, encoding='utf-8'))
                
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
            hasInsert = 1
    except IntegrityError:
        """
        duplicate value
        """
        if i==1 and feedObj.priority != 100:
            feedObj.priority = feedObj.priority+1
            duplicate=1
    
    except _mysql_exceptions.Warning:
        print feedObj
    
    finally:
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
        feedObj.lock = False
        feedObj.save()
    
    if hasInsert:
        from django.conf import settings
        change=os.path.join(settings.SITE_ROOT, '../jsserver/change.txt')
        file = open(change, 'w+')
        file.write('hello')
        file.close()
    
    