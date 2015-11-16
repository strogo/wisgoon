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
    if size <= 120:
        fit_size = 64
    else:
        fit_size = 210

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
    ava_dict = {}

    try:
        profile = Profile.objects.only('avatar', 'version')\
            .get(user_id=user_id)
    except Profile.DoesNotExist:
        profile = None

    if profile:
        if profile.version == Profile.AVATAT_MIGRATED and settings.DEBUG:
            url_prefix = "http://wisgoon.com/media/"
        else:
            url_prefix = "/media/"

        try:
            if profile and profile.avatar:
                url = None
                if profile.version == Profile.AVATAR_OLD_STYLE or\
                        profile.version == Profile.AVATAR_NEW_STYLE:
                    profile.store_avatars(update_model=True)
                    from pin.tasks import migrate_avatar_storage
                    migrate_avatar_storage.delay(profile_id=profile.id)

                if fit_size == 64:
                    url = '%s%s' % (url_prefix, profile.get_avatar_64_str())
                else:
                    url = '%s%s' % (url_prefix, profile.avatar)
                if url:
                    return url
        except Exception, e:
            print str(e)

    glob_avatar = daddy_avatar("", size)
    ava_dict[size] = glob_avatar
    cache.set(ava_str, ava_dict, 60 * 60 * 1)
    return glob_avatar
