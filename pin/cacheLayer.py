from django.core.cache import cache


class UserDataCache(object):
    key_name = "C:L:U:%(user_id)s"  # cache layer user 1
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
        from django.contrib.auth import get_user_model
        User = get_user_model()
        try:
            u = User.objects.only('username').get(id=user_id)
            username = u.username
        except User.DoesNotExist:
            username = "Unknown"
        cache.set(keyname, username, cls.ttl)
        cls.cache_in_class[keyname] = username
        return username


class CategoryDataCache(object):
    key_name = "C:L:C:%(category_id)s"  # cache layer category 1
    ttl = 86400

    cache_in_class = {}

    @classmethod
    def get_cat_json(cls, category_id):
        keyname = cls.key_name % {'category_id': category_id}
        if keyname in cls.cache_in_class:
            return cls.cache_in_class[keyname]
        jcc = cache.get(keyname)
        if jcc:
            return jcc

        from pin.models import Category

        cat = Category.objects.get(id=category_id)
        cat_json = {
            'id': cat.id,
            'image': cat.image.url,
            'resource_uri': "/pin/apic/category/" + str(cat.id) + "/",
            'title': cat.title,
        }
        cache.set(keyname, cat_json, cls.ttl)
        cls.cache_in_class[keyname] = cat_json
        return cat_json
