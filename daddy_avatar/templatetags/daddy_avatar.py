from django.template import Library
from django.utils.hashcompat import md5_constructor
from django.conf import settings
import os
import urllib

register = Library()

@register.filter
def daddy_avatar(user_email, size=200):
    ahash = md5_constructor(user_email).hexdigest()
    
    hash_dir = os.path.join(settings.MEDIA_ROOT, 'daddy_avatar/%d' % size)
    ospath = os.path.join(settings.MEDIA_ROOT, '%s/%s_%d.jpg'%(hash_dir, ahash, size))
    gravatar_url = "http://www.gravatar.com/avatar/%s.jpg/?s=%d" % (ahash, size)
    
    media_avatar = os.path.join(settings.MEDIA_URL, 'daddy_avatar/%d/%s_%d.jpg'%(size, ahash, size))
    
    if not os.path.exists(hash_dir):
        os.makedirs(hash_dir)
        
    if not os.path.exists(ospath):
        urllib.urlretrieve(gravatar_url, ospath)
        
    return media_avatar
        