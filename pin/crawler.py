import httplib
import lxml.html
import socket
import urllib2
import urlparse

from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

socket.setdefaulttimeout(10)


def get_url_content(url):
    try:
        f = urllib2.urlopen(url)
        content = f.read()
        return content
    except Exception:
        return 0
    return 0


def check_content_type(url):
    o = urlparse.urlparse(url)
    conn = httplib.HTTPConnection(o.netloc)
    conn.request("HEAD", o.path)
    res = conn.getresponse()
    content_type = res.getheader('content-type')
    if content_type and content_type.startswith('image'):
        return 'image'
    else:
        return 'text'

    return 'text'


def validate_url(url):
    valid_url = URLValidator()
    try:
        valid_url(url)
    except ValidationError:
        return 0
    return 1


def get_images(url):
    if validate_url(url):
        images = []
        if check_content_type(url) == 'image':
            images.append(url)
        else:
            content = get_url_content(url)
            if content == 0:
                return 0
            tree = lxml.html.fromstring(content)
            for image in tree.xpath("//img/@src"):
                if not image.startswith('http://'):
                    image = urlparse.urljoin(url, image)
                if image not in images:
                    images.append(image)

        return images
    return 0
