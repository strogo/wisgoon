import sys

sys.path.append('/var/www/html/feedreader/')
sys.path.append('/var/www/html/')

from django.core.management import setup_environ 
import settings
setup_environ(settings)

from rss.models import Feed
from feedreader.parser import parse_feed

feedObj = Feed.objects.filter(lock=False).all().order_by('-last_fetch')

for i in feedObj:
    parse_feed(i)
