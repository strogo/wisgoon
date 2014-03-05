from django.core.cache import cache
from django.contrib.auth.models import User
from pin.forms import PinForm
from pin.models import Category

from pin.mycache import caching


def pin_form(request):
    return {'pin_form': PinForm}


def pin_categories(request):
    cats = caching(Category.objects.all(), 'pin_cats')
    return {'cats': cats}


def is_super_user(request):
    return False
    #print "re user", request.user
    #if request.user.is_superuser:
    #    return {'is_super_user': True}

    #return {'is_super_user': False}


def user__id(request):
    return {'user__id': request.user.id}
