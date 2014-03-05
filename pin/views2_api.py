#-*- coding: utf-8 -*-
import json
from django.http import HttpResponse
from django.core.cache import cache

from sorl.thumbnail import get_thumbnail

from pin.tools import userdata_cache, AuthCache, CatCache
from pin.models import Post, Category

class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        if isinstance(obj, FieldFile):
            return str(obj)

        return json.JSONEncoder.default(self, obj)

def get_thumb(o_image, thumb_size, thumb_quality):
    c_str = "s2%s_%s_%s" % (o_image, thumb_size, thumb_quality)
    img_cache = cache.get(c_str)
    if img_cache:
        imo = img_cache
        print imo, "cache"
    else:
        try:
            im = get_thumbnail(o_image,
                               thumb_size,
                               quality=thumb_quality,
                               upscale=False)
            imo = {
                'thumbnail': im.url,
                'hw': "%sx%s" % (im.height, im.width)
            }
            cache.set(c_str, imo, 8600)
        except:
            imo = ""
        print imo
    return imo

def get_cat(cat_id):
    cat_cache_str = "cat_%s" % cat_id
    cat_cache = cache.get(cat_cache_str)
    if cat_cache:
        return cat_cache

    cat = Category.objects.get(id=cat_id)
    cache.set(cat_cache_str, cat, 8600)
    return cat

def post(request):
    data = {}
    data['meta'] = {'limit': 10,
                        'next': '',
                        'offset': 0,
                        'previous': '',
                        'total_count': 1000
                        }

    objects_list = []
    filters = {}
    filters.update(dict(status=1))
    before = request.GET.get('before', None)
    category_id = request.GET.get('category_id', None)
    popular = request.GET.get('popular', None)

    if category_id:
            category_ids = category_id.replace(',', ' ').split(' ')
            filters.update(dict(category_id__in=category_ids))

    if before:
        filters.update(dict(id__lt=before))

    if popular:
        self.show_ads = False
        date_from = None
        dn = datetime.datetime.now()
        if popular == 'month':
            date_from = dn - datetime.timedelta(days=30)
        elif popular == 'lastday':
            date_from = dn - datetime.timedelta(days=1)
        elif popular == 'lastweek':
            date_from = dn - datetime.timedelta(days=7)
        elif popular == 'lasteigth':
            date_from = dn - datetime.timedelta(hours=8)

        if date_from:
            start_from = time.mktime(date_from.timetuple())
            filters.update(dict(timestamp__gt=start_from))
    
    print str(filters)
    posts = Post.objects.filter(**filters).order_by('-id')

    for p in posts:
        o = {}
        o['id'] = p.id
        o['text'] = p.text
        o['cnt_comment'] = 0 if p.cnt_comment == -1 else p.cnt_comment
        o['image'] = p.image

        av = AuthCache.avatar(user_id=p.user_id)
        o['user_avatar'] = AuthCache.avatar(user_id=p.user_id)[1:]
        o['user_name'] = AuthCache.get_username(user_id=p.user_id)

        o['user'] = p.user_id
        o['url'] = 'v'
        o['like'] = p.cnt_like
        o['likers'] = None
        o['like_with_user'] = True

        o['permalink'] = "/pin/%d/" % p.id
        o['resource_uri'] = "/pin/api/post/%d/" % p.id

        thumb_size = request.GET.get('thumb_size', "100x100")
        thumb_quality = 99

        o_image = p.image

        imo = get_thumb(o_image, thumb_size, thumb_quality)

        if imo:
            o['thumbnail'] = imo['thumbnail'].replace('/media/', '')
            o['hw'] = imo['hw']

        cat = get_cat(cat_id=p.category_id)
        o['category'] = {
            'id': cat.id,
            'image': "/media/" + str(cat.image),
            'resource_uri': "/pin/apic/category/"+str(cat.id)+"/",
            'title': cat.title,
        }
        objects_list.append(o)

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)