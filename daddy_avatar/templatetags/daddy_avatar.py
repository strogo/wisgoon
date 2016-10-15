import os

from django.template import Library
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth import get_user_model

from user_profile.models import Profile

register = Library()
User = get_user_model()


@register.filter
def daddy_avatar(user_email, size=165):
    media_avatar = os.path.join(settings.MEDIA_URL, 'assets/img/default_avatar1.jpg')
    return media_avatar


@register.filter
def get_avatar(user, size=165):
    if size <= 120:
        fit_size = 64
    else:
        fit_size = 210

    class UserGeneric(object):
        pass

    if not user:
        return daddy_avatar('', size)

    u = None

    if isinstance(user, (unicode)):
        user = int(user)

    if isinstance(user, (int, long)):
        u = UserGeneric()
        u.id = int(user)

    if isinstance(user, User):
        u = user

    if not u:
        glob_avatar = daddy_avatar("", size)
        return glob_avatar

    user_id = u.id

    ava_str = settings.AVATAR_CACHE_KEY.format(user_id)
    ava_dict = cache.get(ava_str, {})

    if fit_size in ava_dict:
        return ava_dict[fit_size]

    try:
        profile = Profile.objects.only('avatar', 'version')\
            .get(user_id=user_id)
    except Profile.DoesNotExist:
        profile = None

    if profile:
        url_prefix = "/media/"

        try:
            if profile and profile.avatar:
                url = None

                if fit_size == 64:
                    url = '%s%s' % (url_prefix, profile.get_avatar_64_str())
                else:
                    url = '%s%s' % (url_prefix, profile.avatar)
                if url:
                    from pin.api_tools import media_abs_url
                    url = media_abs_url(url, check_photos=True)
                    ava_dict[fit_size] = url
                    cache.set(ava_str, ava_dict, 86400)
                    return url
        except Exception, e:
            print str(e)

    glob_avatar = daddy_avatar("", size)
    ava_dict[size] = glob_avatar
    cache.set(ava_str, ava_dict, 60 * 60 * 1)
    return glob_avatar
