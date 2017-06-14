from django.core.cache import caches

cache = caches['cache_layer']


class PostCacheLayer(object):
    CACHE_KEY = "pcl:1.7:{}"
    POST_ID = None
    TTL = 14400
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

    def delete(self):
        cache.delete(self.CACHE_KEY)

    def like_change(self, cnt_like):
        if not self.data:
            return
        from tools import get_last_likers
        self.data['last_likers'] = get_last_likers(post_id=self.POST_ID)
        self.data['cnt_like'] = cnt_like
        self.set(self.data)

    def comment_change(self, cnt_comment):
        if not self.data:
            return
        from tools import get_last_comments
        self.data['last_comments'] = get_last_comments(post_id=self.POST_ID)
        self.data['cnt_comment'] = cnt_comment
        self.set(self.data)

    def delete_comment(self, cnt_comment):
        if not self.data:
            return
        from tools import get_last_comments
        self.data['last_comments'] = get_last_comments(post_id=self.POST_ID)
        total_comment = cnt_comment - 1
        if total_comment > 0:
            self.data['cnt_comment'] = total_comment
        else:
            self.data['cnt_comment'] = 0
        self.set(self.data)

    def post_change(self, post):
        if not self.data:
            return
        from tools import category_get_json, get_post_tags
        self.data['category'] = category_get_json(cat_id=post.category_id)
        self.data['text'] = post.text
        self.data['url'] = post.url
        self.data['tags'] = get_post_tags(post)
        self.set(self.data)

    def show_in_default_change(self, status):
        if not self.data:
            return

        self.data['show_in_default'] = status
        self.set(self.data)

    def invalid_url(self, url):
        import requests
        requests.request("PURGE", url.replace('&', ''))


class Book():
    pass
