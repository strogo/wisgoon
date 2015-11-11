import os

from django.template import Library
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User

from sorl.thumbnail import get_thumbnail
from user_profile.models import Profile

register = Library()


@register.filter
def daddy_avatar(user_email, size=165):
    media_avatar = os.path.join(settings.MEDIA_URL, 'default_avatar1.jpg')
    return media_avatar


@register.filter
def get_avatar(user, size=165):
    class UserGeneric(object):
        pass

    if not user:
        return daddy_avatar('', size)

    if isinstance(user, (unicode)):
        user = int(user)

    if isinstance(user, (int, long)):
        u = UserGeneric()
        u.id = int(user)

    if isinstance(user, User):
        u = user

    user_id = u.id

    ava_str = "avatar3210u_%d" % (user_id)

    ava_dict = cache.get(ava_str)

    if ava_dict:

        if size in ava_dict:
            return ava_dict[size]
        else:
            try:
                profile = Profile.objects.only('avatar').get(user_id=user_id)
            except Profile.DoesNotExist:
                profile = None

            if profile:
                if profile.avatar:
                    t_size = '%sx%s' % (size, size)
                    try:
                        im = get_thumbnail(profile.avatar, t_size, crop='center', quality=99)
                        ava_dict[size] = im.url
                        cache.set(ava_str, ava_dict, 60 * 60 * 1)
                        return im.url
                    except Exception, e:
                        print "daddy_avatar line 96: ", str(e)

    else:
        ava_dict = {}
        try:
            profile = Profile.objects.only('avatar').get(user_id=user_id)
        except Profile.DoesNotExist:
            profile = None

        if profile:
            t_size = '%sx%s' % (size, size)
            try:
                im = get_thumbnail(profile.avatar, t_size, crop='center', quality=99)
                ava_dict[size] = im.url
                cache.set(ava_str, ava_dict, 60 * 60 * 1)
                return im.url
            except Exception, e:
                pass

    glob_avatar = daddy_avatar("", size)
    ava_dict[size] = glob_avatar
    cache.set(ava_str, ava_dict, 60 * 60 * 1)
    return glob_avatar
