from ban.models import Blog
import urllib2

from ban_parse import get_links

def init():
    for provider in Blog.PROVIDERS:
        url = "http://www.%s" % ( provider[1])
        
        html = urllib2.urlopen(url)
        get_links(html.read())
        