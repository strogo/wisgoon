import time
import redis
from pin.utils import patch
from django.conf import settings

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


class QueryCacheMiddleware:
    def process_request(self, request):
        pass
        patch()


class UrlRedirectMiddleware:

    def process_request(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # print "ip is:", ip
        user_id = ip
        now = int(time.time())
        expires = now + (5 * 60) + 10
        all_users_key = 'online-users/%d' % (now // 60)
        user_key = 'user-activity/%s' % user_id
        p = r_server.pipeline()
        p.sadd(all_users_key, user_id)
        p.set(user_key, now)
        p.expireat(all_users_key, expires)
        p.expireat(user_key, expires)
        p.execute()

        # current = int(time.time()) // 60
        # minutes = xrange(5)

        # onlines = r_server.sunion(['online-users/%d' % (current - x)
        #                  for x in minutes])

        # print len(onlines)

