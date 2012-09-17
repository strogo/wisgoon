import lxml.html
from urlparse import urlparse
from ban.models import Blog

def get_links(content):
    
    p_list = []
    for p in Blog.PROVIDERS:
        p_list.append(p[1])
    
    h = lxml.html.fromstring(content)
    urls = h.xpath('//a/@href')
    for url in urls:
        o = urlparse(url)
        try :
            if o.netloc.index(p_list):
                print o.netloc
        except ValueError:
            print list(Blog.PROVIDERS)
