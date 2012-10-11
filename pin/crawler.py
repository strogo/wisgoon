import socket
import urllib2
import lxml.html
import urlparse



socket.setdefaulttimeout(10)


def get_url_content(url):
    try:
        f = urllib2.urlopen(url)
        content = f.read()
        return content
    except:
        return 0

def get_images(url):
    content = get_url_content(url)
    if content == 0:
        return 0
    tree = lxml.html.fromstring(content)
    images = []
    for image in tree.xpath("//img/@src"):
        if not image.startswith('http://'):
            image = urlparse.urljoin(url, image)
        images.append(image)
    
    return images
