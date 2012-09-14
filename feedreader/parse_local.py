import sys
import os

#sys.path.append('/var/www/html/feedreader/')
#sys.path.append('/var/www/html/')
#sys.path.append('/home/vahid/workspace/wisgoon.com/feedreader')
#sys.path.append('/home/vahid/workspace/wisgoon.com')

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__),'../'))

from django.core.management import setup_environ 
import settings_local 
setup_environ(settings_local)

from rss.models import Feed
from feedreader.parser import parse_feed

feedObj = Feed.objects.all()

for i in feedObj:
    parse_feed(i)
