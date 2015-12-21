from django.core.cache import get_cache

cache = get_cache('cache_layer')


class PostCacheLayer(object):
    CACHE_KEY = "p:c:l:v1:{}"
    POST_ID = None
    TTL = 86400
    data = None

    def __init__(self, post_id):
        self.POST_ID = post_id
        self.CACHE_KEY = self.CACHE_KEY.format(post_id)
        self.__get_data()

    def get(self):
        cached_data = cache.get(self.CACHE_KEY)
        if cached_data:
            return cached_data
        return False

    def __get_data(self):
        if not self.data:
            self.data = self.get()

        return self.data

    def set(self, data):
        cache.set(self.CACHE_KEY, data, self.TTL)

    def like_change(self, cnt_like):
        if not self.data:
            return
        from tools import get_last_likers
        self.data['last_likers'] = get_last_likers(post_id=self.POST_ID)
        self.data['cnt_like'] = cnt_like
        self.set(self.data)


class Book():
    pass
