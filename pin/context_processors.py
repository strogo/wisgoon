import datetime

from pin.forms import PinForm
from pin.models import Category
from pin.model_mongo import MonthlyStats

from pin.mycache import caching


def pin_form(request):
    return {'pin_form': PinForm}


def pin_categories(request):
    cats = caching(Category.objects.all(), 'pin_cats')
    return {'cats': cats}


def today_stats(request):
    d = str(datetime.date.today())
    m = MonthlyStats.objects(date=d)
    ma = {}
    for mm in m:
        ma[mm.object_type] = mm.count
    # print ma
    return {'stats': ma}


def is_super_user(request):
    #return {'is_super_user': False}
    #print "re user", request.user
    if request.user.is_superuser:
        return {'is_super_user': True}

    return {'is_super_user': False}


def user__id(request):
    return {'user__id': request.user.id}
