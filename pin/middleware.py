import time
import redis
from pin.utils import patch
from django.conf import settings

from django import http

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


try:
    XS_SHARING_ALLOWED_ORIGINS = settings.XS_SHARING_ALLOWED_ORIGINS
    XS_SHARING_ALLOWED_METHODS = settings.XS_SHARING_ALLOWED_METHODS
except:
    XS_SHARING_ALLOWED_ORIGINS = '*'
    XS_SHARING_ALLOWED_METHODS = ['POST', 'GET', 'OPTIONS', 'PUT', 'DELETE']


class XsSharing(object):

    def process_request(self, request):

        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            response['Access-Control-Allow-Origin'] = XS_SHARING_ALLOWED_ORIGINS
            response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS ) 

            return response

        return None

    def process_response(self, request, response):
        # Avoid unnecessary work
        if response.has_header('Access-Control-Allow-Origin'):
            return response

        response['Access-Control-Allow-Origin']  = XS_SHARING_ALLOWED_ORIGINS 
        response['Access-Control-Allow-Methods'] = ",".join( XS_SHARING_ALLOWED_METHODS )

        return response


class QueryCacheMiddleware:
    def process_request(self, request):
        pass
        patch()


class UrlRedirectMiddleware:

    def process_request(self, request):
        pass
        # x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        # if x_forwarded_for:
        #     ip = x_forwarded_for.split(',')[0]
        # else:
        #     ip = request.META.get('REMOTE_ADDR')

        # # print "ip is:", ip
        # user_id = ip
        # now = int(time.time())
        # expires = now + (5 * 60) + 10
        # all_users_key = 'online-users/%d' % (now // 60)
        # user_key = 'user-activity/%s' % user_id
        # p = r_server.pipeline()
        # p.sadd(all_users_key, user_id)
        # p.set(user_key, now)
        # p.expireat(all_users_key, expires)
        # p.expireat(user_key, expires)
        # p.execute()

        # current = int(time.time()) // 60
        # minutes = xrange(5)

        # onlines = r_server.sunion(['online-users/%d' % (current - x)
        #                  for x in minutes])

        # print len(onlines)

