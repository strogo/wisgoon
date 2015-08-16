from django.core.cache import cache


class UserDataCache(object):
    key_name = "C:L:U:%(user_id)s"
    ttl = 86400

    cache_in_class = {}

    @classmethod
    def get_user_name(cls, user_id):
        keyname = cls.key_name % {'user_id': user_id}
        if keyname in cls.cache_in_class:
            return cls.cache_in_class[keyname]
        ce = cache.get(keyname)
        if ce:
            return ce
        from django.contrib.auth.models import User
        try:
            u = User.objects.only('username').get(id=user_id)
            username = u.username
        except User.DoesNotExist:
            username = "Unknown"
        cache.set(keyname, username, cls.ttl)
        cls.cache_in_class[keyname] = username
        return username
