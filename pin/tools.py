import os
import time
from datetime import datetime
from django.core.cache import cache
from django.conf import settings

from pin.templatetags.pin_tags import get_username
from daddy_avatar.templatetags import daddy_avatar

user_keys = {}
USERDATA_TIMEOUT = 300


def create_filename(filename):
    d = datetime.now()
    folder = "%d/%d" % (d.year, d.month)
    paths = []
    paths.append("%s/pin/temp/o/" % (settings.MEDIA_ROOT))
    paths.append("%s/pin/temp/t/" % (settings.MEDIA_ROOT))
    paths.append("%s/pin/images/o/" % (settings.MEDIA_ROOT))
    paths.append("%s/pin/images/t/" % (settings.MEDIA_ROOT))
    for path in paths:
        abs_path = "%s%s" % (path, folder)
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
    filestr = "%s/%f" % (folder, time.time())
    filestr = filestr.replace('.', '')
    filename = "%s%s" % (filestr, os.path.splitext(filename)[1])
    return filename


def userdata_cache(user, field=None, size=100):
    cache_key = 'user_%s' % user

    if cache_key in user_keys:
        data = user_keys[cache_key]
    else:
        data = cache.get(cache_key)

    if data:
        if field is not None:
            return data[field]

        return data
    else:
        avatar = daddy_avatar.get_avatar(user, size=size)
        username = get_username(user)

        value = [avatar, username]
        user_keys[cache_key] = value
        cache.set(cache_key, value, USERDATA_TIMEOUT)

        if field is not None:
            return value[field]

        return value

    return []
