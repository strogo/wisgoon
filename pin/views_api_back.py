import json
import datetime
from time import mktime

from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator, InvalidPage
from django.core.urlresolvers import reverse
from django.db.models.fields.files import FieldFile
from django.core.cache import cache
from django.contrib.auth.models import User
from django.conf import settings

from pin.models import Post

CACHE_AVATAR = 0
CACHE_USERNAME = 1


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        if isinstance(obj, FieldFile):
            return str(obj)

        return json.JSONEncoder.default(self, obj)


def tone_count(tone_q):
    if cache.get("tone_count", None):
        return cache.get("tone_count")

    count = tone_q.count()
    cache.set("tone_count", count, settings.CACHE_TONE_COUNT)
    return count


class DaddyResource(object):
    ROW_PER_PAGE = 10

    def data(self):
        return self.queryset

    def count(self):
        cache_str = "%s_count" % (self.resource_name)
        if cache.get(cache_str, None):
            return cache.get(cache_str)

        count = self.queryset.count()
        cache.set(cache_str, count, settings.CACHE_TONE_COUNT)
        return count

    def paging(self, request):
        paginator = Paginator(self.queryset, self.ROW_PER_PAGE)
        try:
            page = paginator.page(int(request.GET.get('page', 1)))
            if page.has_next():
                self.next_page = '%s?page=%s' % (reverse(self.resource_url),
                                                 page.next_page_number())
            else:
                self.next_page = None

            if page.has_previous():
                self.previous_page = '%s?page=%s' % (reverse(self.resource_url),
                                                     page.previous_page_number())
            else:
                self.previous_page = None
        except InvalidPage:
            raise Http404("Sorry, no results on that page.")

        return page


class ToneResource(DaddyResource):
    fields = ['cnt_download', 'cnt_like', 'create_time', 'id', 'title', 'file_url']
    queryset = None
    resource_name = 'tone'
    resource_url = 'tone_api'

    request = None
    request_page = 1
    cache_hash_list = ""
    cached_list = None

    paginator = None
    page = None
    next_page = None
    previous_page = None


    def __init__(self, request):
        self.request_page = int(request.GET.get('page', 1))
        self.cache_hash_list = "tone_list_json_%d" % (self.request_page)
        cex = cache.get(self.cache_hash_list, None)
        if cex:
            self.cached_list = cex
        else:
            self.request = request
            self.queryset = Post.objects.order_by('-id').all()

    def get_json(self):
        if self.cached_list:
            print "getting data from cache"
            return self.cached_list

        data = {}
        tones = self.data()
        tones.count = self.count()

        page = self.paging(self.request)

        data['meta'] = {'limit': self.ROW_PER_PAGE,
                        'next': self.next_page,
                        'offset': 0,
                        'previous': self.previous_page,
                        'total_count': self.count()
                        }

        objects_list = []

        for t in page.object_list:
            o = {}
            for s in self.fields:
                o[s] = getattr(t, s)

            user_id = int(getattr(t, 'user_id'))
            user = get_user_from_cache(user_id)
            o['user'] = {'id': user.id,
                         'avatar': userdata_cache(user, CACHE_AVATAR),
                         'name': userdata_cache(user, CACHE_USERNAME),
                         }
            objects_list.append(o)

        data['objects'] = objects_list
        json_data = json.dumps(data, cls=MyEncoder)
        cache.set(self.cache_hash_list, json_data, settings.CACHE_TONE_JSON)
        return json_data


def tone(request):
    tr = ToneResource(request)
    return HttpResponse(tr.get_json())


def post(request):
    tr = ToneResource(request)
    return HttpResponse(tr.get_json())