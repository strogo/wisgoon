import sys
import urllib2
from urllib2 import HTTPError
import lxml.html

sys.path.append('/var/www/html/feedreader/')
sys.path.append('/var/www/html/')
sys.path.append('/home/vahid/workspace/wisgoon.com/feedreader')
sys.path.append('/home/vahid/workspace/wisgoon.com/rss')
sys.path.append('/home/vahid/workspace/wisgoon.com')

from django.core.management import setup_environ 
import settings_local
setup_environ(settings_local)

from avval.models import Bank

for i in range(498660,498665):
    url = "http://www.avval.ir/%d" % i
    try:
        response = urllib2.urlopen(url)
        html_co = response.read()
        
        tree = lxml.html.fromstring(html_co)
        elements = tree.get_element_by_id('entity-left')
        for el in elements:
            html_co = el.text_content()
        
        b=Bank()
        b.primary=i
        b.block = html_co.encode('utf-8')
        b.save()
        
    except HTTPError:
        pass