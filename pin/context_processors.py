import datetime

from django.conf import settings
from django.core.cache import cache

from pin.forms import PinForm
from pin.models import Category, SubCategory, SystemState
from pin.model_mongo import MonthlyStats

from pin.mycache import caching


def static_version(request):
    return {'STATIC_VERSION': settings.STATIC_VERSION}


def static_cdn(request):
    return {'STATIC_CDN': settings.STATIC_CDN}


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

    cache.set("today_stats", ma, 60)

    return {'stats': ma}


def is_super_user(request):
    if request.user.is_superuser:
        return {'is_super_user': True}

    return {'is_super_user': False}


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


def global_values(request):
    return {
        'SITE_URL': settings.SITE_URL,
        'SITE_NAME_FA': settings.SITE_NAME_FA,
        'SITE_NAME_EN': settings.SITE_NAME_EN,
        'SITE_DESC': settings.SITE_DESC,
        'DEBUG': settings.DEBUG,
        'DISPLAY_AD': settings.DISPLAY_AD,
        'SITE_URL_NAME': settings.SITE_URL_NAME
    }


def system_read_only(request):
    state = cache.get(SystemState.CACHE_NAME)
    if state is None:
        try:
            sys_state = SystemState.objects.get(id=1)
            state = sys_state.read_only
        except SystemState.DoesNotExist:
            sys_state = SystemState.objects.create(read_only=False)
            state = sys_state.read_only
    return {'READ_ONLY': state}
