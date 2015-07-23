from django.core.cache import cache


class UserNameCache(object):
    key_name = "C:L:U:%(user_id)s"
    ttl = 86400

    @classmethod
    def get_user_name(cls, user_id):
        keyname = cls.key_name % {'user_id': user_id}
        ce = cache.get(keyname)
        if ce:
            return ce
        from django.contrib.auth.models import User
        u = User.objects.only('username').get(id=user_id)
        cache.set(keyname, u.username, cls.ttl)
        return u.username
