import os
import urllib

from django.template import Library
from django.utils.hashcompat import md5_constructor
from django.conf import settings
from django.contrib.auth.models import User

from sorl.thumbnail import get_thumbnail
from user_profile.models import Profile

register = Library()


@register.filter
def daddy_avatar(user_email, size=200):
    ahash = md5_constructor(user_email).hexdigest()
    hash_dir = os.path.join(settings.MEDIA_ROOT, 'daddy_avatar/%d' % size)
    ospath = '%s/%s_%d.jpg' % (hash_dir, ahash, size)
    gravatar_url = "http://www.gravatar.com/avatar/%s.jpg/?s=%d" % (ahash, size)
    media_avatar = os.path.join(settings.MEDIA_URL, 'daddy_avatar/%d/%s_%d.jpg' % (size, ahash, size))
    if not os.path.exists(hash_dir):
        os.makedirs(hash_dir)
    if not os.path.exists(ospath):
        urllib.urlretrieve(gravatar_url, ospath)
    return media_avatar


@register.filter
def get_avatar(user, size=200):
    if not user:
        return daddy_avatar('', size)

    if isinstance(user, int):
        user = User.objects.only('email').get(pk=user)

    try:
        profile = Profile.objects.only('avatar').get(user=user)
        if profile.avatar:
            t_size = '%sx%s' % (size, size)
            im = get_thumbnail(profile.avatar, t_size, crop='center', quality=99)
            return im.url
    except:
        pass

    return daddy_avatar(user.email, size)
