import os
import urllib

from django.template import Library
from django.utils.hashcompat import md5_constructor
from django.core.cache import cache
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

    if isinstance(user, (unicode)):
        user = int(user)

    if isinstance(user, (int, long)):
        #user = User.objects.only('email').get(pk=user)
        user_str = "user_%d" % (user)
        user_cache = cache.get(user_str)
        if user_cache:
            user = user_cache
        else:
            try:
                user = User.objects.only('email').get(pk=user)
                cache.set(user_str, user, 60 * 60 * 24)
            except:
                return 'None'

    ava_str = "avatar3210u_%d" % (user.id)
    # ava_dict = {}
    # try:
    ava_dict = cache.get(ava_str)
    # print "ava cache is:", ava_dict, ava_str, size
    if ava_dict:
        # print "step 1"

        if size in ava_dict:
            # print "step 1.1"
            #print "get avatar from cache", ava_dict
            return ava_dict[size]
        else:
            # print "step 1.2"
            profile = Profile.objects.only('avatar').get(user=user)
            
            if profile.avatar:
                # print "step 1.2.1"
                t_size = '%sx%s' % (size, size)
                try:
                    im = get_thumbnail(profile.avatar, t_size, crop='center', quality=99)
                    ava_dict[size] = im.url
                    cache.set(ava_str, ava_dict, 60 * 60 * 1)
                    return im.url
                except Exception, e:
                    print "daddy_avatar line 96: ", str(e)
    # except Exception, e:
    #     print str(e)
    else:
        # print "step 2"
        ava_dict = {}
        # print "step 2.1"
        try:
            profile = Profile.objects.only('avatar').get(user=user)
        except Profile.DoesNotExist:
            profile = None
        
        if profile:
            # print "step 2.2.1"
            t_size = '%sx%s' % (size, size)
            try:
                im = get_thumbnail(profile.avatar, t_size, crop='center', quality=99)
                ava_dict[size] = im.url
                cache.set(ava_str, ava_dict, 60 * 60 * 1)
                return im.url
            except Exception, e:
                print "daddy_avatar line 94: ", str(e)

    glob_avatar = daddy_avatar(user.email, size)
    ava_dict[size] = glob_avatar
    cache.set(ava_str, ava_dict, 60 * 60 * 1)
    return glob_avatar
