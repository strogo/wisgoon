#-*- coding: utf-8 -*-
import json
import datetime
import time
from hashlib import md5

from django.http import HttpResponse
from django.core.cache import cache
from django.conf import settings

from sorl.thumbnail import get_thumbnail

from pin.tools import userdata_cache, AuthCache, CatCache
from pin.models import Post, Category, Likes, Stream, Follow
from pin.model_mongo import Notif

from daddy_avatar.templatetags.daddy_avatar import get_avatar


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        """if isinstance(obj, FieldFile):
            return str(obj)"""

        return json.JSONEncoder.default(self, obj)


def get_thumb(o_image, thumb_size, thumb_quality):
    c_str = "s2%s_%s_%s" % (o_image, thumb_size, thumb_quality)
    img_cache = cache.get(c_str)
    if img_cache:
        imo = img_cache
        #print imo, "cache"
    else:
        try:
            im = get_thumbnail(o_image,
                               thumb_size,
                               quality=settings.API_THUMB_QUALITY,
                               upscale=False)
            imo = {
                'thumbnail': im.url,
                'hw': "%sx%s" % (im.height, im.width)
            }
            cache.set(c_str, imo, 8600)
        except:
            imo = ""
        #print imo
    return imo


def get_cat(cat_id):
    cat_cache_str = "cat_%s" % cat_id
    cat_cache = cache.get(cat_cache_str)
    if cat_cache:
        return cat_cache

    cat = Category.objects.get(id=cat_id)
    cache.set(cat_cache_str, cat, 8600)
    return cat


def post_item(request, item_id):
    thumb_size = request.GET.get('thumb_size', "100x100")
    thumb_quality = 99

    cache_pi_str = "post_item_%s_%s" % (item_id, thumb_size)
    p = cache.get(cache_pi_str)
    if p:
        return HttpResponse(p)

    try:
        p = Post.objects.values('id', 'image').get(id=item_id)
    except Exception, e:
        print str(e)
        return HttpResponse('{}')

    data = {}

    o_image = p['image']

    imo = get_thumb(o_image, thumb_size, settings.API_THUMB_QUALITY)

    if imo:
        data['id'] = p['id']
        data['thumbnail'] = imo['thumbnail'].replace('/media/', '')
        data['hw'] = imo['hw']

    json_data = json.dumps(data, cls=MyEncoder)
    cache.set(cache_pi_str, json_data, 86400)
    return HttpResponse(json_data)


def post(request):
    #print "we are in post"
    data = {}
    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    objects_list = []
    filters = {}
    cur_user = None
    cache_ttl = 120
    filters.update(dict(status=Post.APPROVED))
    before = request.GET.get('before', None)
    category_id = request.GET.get('category_id', None)
    popular = request.GET.get('popular', None)
    just_image = request.GET.get('just_image', 0)
    user_id = request.GET.get('user_id', None)

    if before:
        sort_by = ['-timestamp']
    else:
        sort_by = ['-is_ads', '-timestamp']

    token = request.GET.get('token', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if category_id:
        category_ids = category_id.replace(',', ' ').split(' ')
        filters.update(dict(category_id__in=category_ids))

    if before:
        filters.update(dict(id__lt=before))

    if user_id:
        filters.update(dict(user_id=user_id))

    if popular:
        cache_ttl = 60 * 60 * 4
        sort_by = ['-cnt_like']
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

    cache_stream_str = "%s_%s" % (str(filters), sort_by)

    cache_stream_name = md5(cache_stream_str).hexdigest()
    #print cache_stream_str, cache_stream_name

    posts = cache.get(cache_stream_name)
    #print cache_stream_str, cache_stream_name, posts
    if before:
        if not posts:
            posts = Post.objects\
                .values('id', 'text', 'cnt_comment', 'timestamp',
                        'image', 'user_id', 'cnt_like', 'category_id')\
                .filter(**filters).order_by(*sort_by)[:10]

            cache.set(cache_stream_name, posts, 86400)
    else:
        posts = Post.objects\
            .values('id', 'text', 'cnt_comment', 'timestamp',
                    'image', 'user_id', 'cnt_like', 'category_id')\
            .filter(**filters).order_by(*sort_by)[:10]
        if not user_id and not category_id:
            hot_post = Post.get_hot(values=True)
            if hot_post:
                posts = list(hot_post) + list(posts)
        #posts.insert(0, {'user_id': 1L, 'text': u' test final', 'image': u'pin/images/o/2014/7/18/3/1405638687140154.JPG', 'cnt_comment': 3L, 'cnt_like': 1L, 'timestamp': 1405638699L, 'category_id': 1L, 'id': 901L})

    for p in posts:
        o = {}
        o['id'] = p['id']
        o['text'] = p['text']
        o['cnt_comment'] = 0 if p['cnt_comment'] == -1 else p['cnt_comment']
        o['image'] = p['image']

        o['user_avatar'] = get_avatar(p['user_id'], size=100)
        o['user_name'] = AuthCache.get_username(user_id=p['user_id'])

        o['user'] = p['user_id']
        o['url'] = 'v'
        o['like'] = p['cnt_like']
        o['likers'] = None
        o['like_with_user'] = False

        o['permalink'] = "/pin/%d/" % p['id']
        o['resource_uri'] = "/pin/api/post/%d/" % p['id']

        if cur_user:
            o['like_with_user'] = Likes.user_in_likers(post_id=p['id'], user_id=cur_user)

        thumb_size = request.GET.get('thumb_size', "100x100")
        thumb_quality = 99

        o_image = p['image']

        imo = get_thumb(o_image, thumb_size, settings.API_THUMB_QUALITY)

        if imo:
            o['thumbnail'] = imo['thumbnail'].replace('/media/', '')
            o['hw'] = imo['hw']

        o['category'] = Category.get_json(cat_id=p['category_id'])
        objects_list.append(o)

    #cache.set(cache_stream_name, posts, cache_ttl)

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def friends_post(request):
    #print "we are in post"

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    next = {
        'url': "/api/post/friends_post/?limit=%s&offset=%s" % (limit, offset+limit),
    }

    data = {}
    data['meta'] = {'limit': 10,
                    'next': next['url'],
                    'offset': offset,
                    'previous': '',
                    'total_count': 1000}

    objects_list = []
    filters = {}
    cur_user = None
    cache_ttl = 120
    filters.update(dict(status=Post.APPROVED))
    before = request.GET.get('before', None)
    user_id = request.GET.get('user_id', None)

    token = request.GET.get('token', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if before:
        s = Stream.objects.get(user=cur_user, post_id=before)
        stream = Stream.objects.filter(user=cur_user, date__lt=s.date)\
            .order_by('-date')[offset:offset+limit]
        sort_by = ['-timestamp']
    else:
        stream = Stream.objects.filter(user=cur_user)\
            .order_by('-date')[offset:offset+limit]
        sort_by = ['-timestamp']

    idis = []
    for p in stream:
        idis.append(int(p.post_id))

    posts = Post.objects\
        .values('id', 'text', 'cnt_comment', 'timestamp',
                'image', 'user_id', 'cnt_like', 'category_id')\
        .filter(id__in=idis).order_by('-id')[:limit]

    for p in posts:
        o = {}
        o['id'] = p['id']
        o['text'] = p['text']
        o['cnt_comment'] = 0 if p['cnt_comment'] == -1 else p['cnt_comment']
        o['image'] = p['image']

        o['user_avatar'] = get_avatar(p['user_id'], size=100)
        o['user_name'] = AuthCache.get_username(user_id=p['user_id'])

        o['user'] = p['user_id']
        o['url'] = 'v'
        o['like'] = p['cnt_like']
        o['likers'] = None
        o['like_with_user'] = False

        o['permalink'] = "/pin/%d/" % p['id']
        o['resource_uri'] = "/pin/api/post/%d/" % p['id']

        if cur_user:
            o['like_with_user'] = Likes.user_in_likers(post_id=p['id'], user_id=cur_user)

        thumb_size = request.GET.get('thumb_size', "100x100")

        o_image = p['image']

        imo = get_thumb(o_image, thumb_size, settings.API_THUMB_QUALITY)

        if imo:
            o['thumbnail'] = imo['thumbnail'].replace('/media/', '')
            o['hw'] = imo['hw']

        o['category'] = Category.get_json(cat_id=p['category_id'])
        objects_list.append(o)

    #cache.set(cache_stream_name, posts, cache_ttl)

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def likes(request):

    before = request.GET.get('before', None)
    post_id = request.GET.get('post_id', None)
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    next = {
        'url': "/api/v1/tone/?limit=%s&offset=%s" % (limit, offset+limit),
    }

    data = {}
    data['meta'] = {'limit': 10,
                    'next': next['url'],
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    objects_list = []
    filters = {}
    cache_ttl = 120

    if post_id:
        filters.update(dict(post_id=post_id))
    else:
        return HttpResponse('fault')

    cache_stream_str = "wislikes_%s_%s_%s" % (str(filters), str(offset), str(limit))

    cache_stream_name = md5(cache_stream_str).hexdigest()
    #print cache_stream_str, cache_stream_name

    post_likes = cache.get(cache_stream_name)
    if not post_likes:
        post_likes = Likes.objects\
            .values('id', 'post_id', 'user_id')\
            .filter(**filters).all()[offset:offset+limit]
        if len(post_likes) == limit:
            #print "store likes in cache"
            cache.set(cache_stream_name, post_likes, 86400)

    for p in post_likes:
        o = {}
        o['post_id'] = p['post_id']

        o['user_avatar'] = get_avatar(p['user_id'], size=100)
        o['user_name'] = AuthCache.get_username(user_id=p['user_id'])

        o['user_url'] = p['user_id']
        o['resource_uri'] = "/pin/api/like/likes/%d/" % p['id']

        objects_list.append(o)

    #cache.set(cache_stream_name, posts, cache_ttl)

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def notif(request):
    #print "we are in post"
    data = {}
    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    objects_list = []
    filters = {}
    cur_user = None
    cache_ttl = 120
    filters.update(dict(status=Post.APPROVED))
    before = request.GET.get('before', None)
    category_id = request.GET.get('category_id', None)
    popular = request.GET.get('popular', None)
    just_image = request.GET.get('just_image', 0)
    user_id = request.GET.get('user_id', None)

    if before:
        sort_by = ['-timestamp']
    else:
        #sort_by = ['-is_ads', '-timestamp']
        sort_by = ['-timestamp']

    token = request.GET.get('api_key', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    notifs = Notif.objects.filter(owner=cur_user).order_by('-date')[:50]

    rf = ['id', 'text', 'cnt_comment', 'image',
          'user_id', 'cnt_like', 'category_id']

    for p in notifs:
        try:
            cur_p = Post.objects.values(*rf).get(id=p.post)
        except Post.DoesNotExist:
            continue
        o = {}
        o['id'] = cur_p['id']
        o['text'] = cur_p['text']
        o['cnt_comment'] = 0 if cur_p['cnt_comment'] == -1 else cur_p['cnt_comment']
        o['image'] = cur_p['image']
        o['date'] = "2014-05-28T20:22:14"

        av = AuthCache.avatar(user_id=cur_p['user_id'])
        #o['user_avatar'] = AuthCache.avatar(user_id=cur_p['user_id'])[1:]
        #o['user_name'] = AuthCache.get_username(user_id=cur_p['user_id'])

        o['post'] = "/pin/api1/post/879/"
        o['post_id'] = cur_p['id']
        o['post_owner_avatar'] = AuthCache.avatar(user_id=cur_p['user_id'])[1:]
        o['post_owner_id'] = cur_p['user_id']
        o['post_owner_user_name'] = AuthCache.get_username(user_id=cur_p['user_id'])

        o['user'] = cur_p['user_id']
        o['type'] = p['type']
        o['like'] = cur_p['cnt_like']
        o['url'] = ""
        o['likers'] = None
        o['like_with_user'] = False

        o['resource_uri'] = "/pin/api/notif/notify/%d/" % cur_p['id']

        if cur_user:
            o['like_with_user'] = Likes.user_in_likers(post_id=cur_p['id'], user_id=cur_user)

        thumb_size = request.GET.get('thumb_size', "100x100")
        thumb_quality = 99

        o_image = cur_p['image']

        imo = get_thumb(o_image, thumb_size, thumb_quality)

        if imo:
            o['thumbnail'] = imo['thumbnail'].replace('/media/', '')
            o['hw'] = imo['hw']

        o['category'] = Category.get_json(cat_id=cur_p['category_id'])

        ar = []
        for ac in p.last_actors():
            ar.append([
                ac,
                AuthCache.get_username(ac)[1:],
                #AuthCache.avatar(ac, size=100)
                get_avatar(ac, size=100)
            ])

        o['actors'] = ar
        from collections import OrderedDict
        o = OrderedDict(sorted(o.items(), key=lambda o: o[0]))

        objects_list.append(o)

    #cache.set(cache_stream_name, posts, cache_ttl)

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def following(request, user_id=1):
    data = {}
    cur_user = None
    follow_cnt = Follow.objects.filter(follower_id=user_id).count()

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    next = {
        'url': "/pin/api/following/%s/?limit=%s&offset=%s" % (user_id, limit, offset+limit),
    }

    data['meta'] = {'limit': limit,
                    'next': next['url'],
                    'offset': offset,
                    'previous': '',
                    'total_count': follow_cnt}

    objects_list = []

    token = request.GET.get('token', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    for fol in Follow.objects.filter(follower_id=user_id)[offset:offset+limit]:
        o = {}
        o['user_id'] = fol.following_id
        o['user_avatar'] = get_avatar(fol.following_id, size=100)
        o['user_name'] = AuthCache.get_username(fol.following_id)

        if cur_user:
            o['follow_by_user'] = Follow.objects\
                .filter(follower_id=cur_user, following_id=fol.following_id).exists()
        else:
            o['follow_by_user'] = False


        objects_list.append(o)

    data['objects'] = objects_list

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)

def follower(request, user_id=1):
    data = {}
    cur_user = None
    follow_cnt = Follow.objects.filter(following_id=user_id).count()

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    next = {
        'url': "/pin/api/followers/%s/?limit=%s&offset=%s" % (user_id, limit, offset+limit),
    }

    data['meta'] = {'limit': limit,
                    'next': next['url'],
                    'offset': offset,
                    'previous': '',
                    'total_count': follow_cnt}

    objects_list = []

    token = request.GET.get('token', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    for fol in Follow.objects.filter(following_id=user_id)[offset:offset+limit]:
        o = {}
        o['user_id'] = fol.follower_id
        o['user_avatar'] = get_avatar(fol.follower_id, size=100)
        o['user_name'] = AuthCache.get_username(fol.follower_id)

        if cur_user:
            o['follow_by_user'] = Follow.objects\
                .filter(follower_id=cur_user, following_id=fol.follower_id).exists()
        else:
            o['follow_by_user'] = False

        objects_list.append(o)

    data['objects'] = objects_list

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)

def search(request):

    limit = request.GET.get('limit', 1)
    start = request.GET.get('start', 0)

    data = {}
    import pysolr
    solr = pysolr.Solr('http://localhost:8983/solr/wisgoon_user', timeout=10)
    query = request.GET.get('q', '')
    if query:
        q_str = "*%s*" % query
        fq = 'username_s:*%s* name_s:*%s*' % (query, query)
        results = solr.search("*:*", fq=fq, rows=limit, start=start, sort="score_i desc")

        data['objects'] = []
        for r in results:
            o = {}
            o['id'] = r['id']
            o['avatar'] = get_avatar(r['id'], 100)
            o['username'] = r['username_s']
            try:
                o['name'] = r['name_s']
            except:
                pass

            data['objects'].append(o)

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)
