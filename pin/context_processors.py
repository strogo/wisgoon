import datetime
import time
import redis

from django.conf import settings
from django.core.cache import cache

from pin.forms import PinForm
from pin.models import Category, SubCategory
from pin.model_mongo import MonthlyStats, UserMeta

from pin.mycache import caching

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


def pin_form(request):
    return {'pin_form': PinForm}


def pin_categories(request):
    cats = caching(Category.objects.all(), 'pin_cats')
    return {'cats': cats}


def media_prefix(request):
    return {'media_prefix': settings.MEDIA_PREFIX}


def today_stats(request):
    c_stats = cache.get("today_stats")
    if c_stats:
        return {'stats': c_stats}

    d = str(datetime.date.today())
    m = MonthlyStats.objects(date=d)
    ma = {}
    for mm in m:
        ma[mm.object_type] = mm.count
    # print ma
    current = int(time.time()) // 60
    minutes = xrange(5)

    ma['onlines'] = len(r_server.sunion(['online-users/%d' % (current - x) for x in minutes]))

    cache.set("today_stats", ma, 300)

    return {'stats': ma}


def is_super_user(request):
    #return {'is_super_user': False}
    #print "re user", request.user
    if request.user.is_superuser:
        return {'is_super_user': True}

    return {'is_super_user': False}


def is_police(request, flat=False):
    try:
        um = UserMeta.objects.get(user=request.user.id)
        if um.is_police():
            if flat:
                return True
            return {'is_police': True}
    except:
        pass

    if flat:
        return False
    return {'is_police': False}


def user__id(request):
    return {'user__id': request.user.id}


def is_mobile(request):
    from pin.tools import is_mobile

    try:
        mobile = is_mobile(request)
    except:
        mobile = False
    return {'is_mobile': mobile}


def subs(request):
    return {'subs': SubCategory.objects.all()}
