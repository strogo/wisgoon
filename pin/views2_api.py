# -*- coding: utf-8 -*-
import json
import datetime
import time
import redis
from hashlib import md5
from pytz import timezone

from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.tokens import default_token_generator

from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from sorl.thumbnail import get_thumbnail

from pin.tools import AuthCache, get_user_ip, get_fixed_ads, log_act
from pin.models import Post, Category, Likes, Follow, Comments, Block
from pin.model_mongo import Notif, Ads

from haystack.query import SearchQuerySet

from daddy_avatar.templatetags.daddy_avatar import get_avatar

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        # if isinstance(obj, datetime.datetime):
        #     return int(mktime(obj.timetuple()))

        """if isinstance(obj, FieldFile):
            return str(obj)"""

        return json.JSONEncoder.default(self, obj)


def notif_count(request):
    cur_user_id = None
    token = request.GET.get('token', '')
    if token:
        cur_user_id = AuthCache.id_from_token(token=token)

    if not cur_user_id:
        return HttpResponseForbidden('Token problem')

    notify = Notif.objects.filter(owner=cur_user_id, seen=False).count()
    return HttpResponse(notify)


def get_thumb(o_image, thumb_size, thumb_quality):
    thumb_size = str(thumb_size)
    im = 00
    c_str = "s2%s_%s_%s" % (o_image, thumb_size, thumb_quality)
    try:
        img_cache = cache.get(c_str)
    except Exception, e:
        print c_str, str(e)
        img_cache = None
    if img_cache:
        imo = img_cache
        # print imo, "cache"
    else:
        try:
            im = get_thumbnail(o_image,
                               thumb_size,
                               quality=settings.API_THUMB_QUALITY,
                               upscale=False)
            # print "after im, im is:", im
            imo = {
                'thumbnail': im.url,
                'hw': "%sx%s" % (im.height, im.width)
            }
            cache.set(c_str, imo, 8600)
        except Exception, e:
            print "exception in get_thumb", str(e), im
            if thumb_size == "500":
                default_image = 'media/noPhoto_max.jpg'
                dfsize = "500x500"
            else:
                default_image = 'media/noPhoto_mini.jpg'
                dfsize = "236x236"

            imo = {
                'thumbnail': default_image,
                'hw': dfsize
            }
    return imo


def get_cat(cat_id):
    cat_cache_str = "cat_%s" % cat_id
    cat_cache = cache.get(cat_cache_str)
    if cat_cache:
        return cat_cache

    cat = Category.objects.get(id=cat_id)
    cache.set(cat_cache_str, cat, 8600)
    return cat


def get_objects_list(posts, cur_user_id, thumb_size, r=None):
    # cache_key = md5(json.dumps(posts)).hexdigest()
    # list_cache_str = "olist_%s" % (cache_key)
    # cache_list = cache.get(list_cache_str)
    # if cache_list:
    #     return cache_list

    objects_list = []
    for p in posts:
        if not p:
            continue
        if p.is_pending():
            continue
        o = {}
        o['id'] = p.id
        o['text'] = p.text
        o['cnt_comment'] = 0 if p.cnt_comment == -1 else p.cnt_comment
        o['image'] = p.image

        o['user_avatar'] = get_avatar(p.user_id, size=100)
        o['user_name'] = AuthCache.get_username(user_id=p.user_id)

        o['timestamp'] = p.timestamp

        o['user'] = p.user_id
        try:
            o['url'] = p.url
        except Exception, e:
            print str(e)
            if r:
                print r.get_full_path()
            o['url'] = None
        o['like'] = p.cnt_like
        o['likers'] = None
        o['like_with_user'] = False
        o['status'] = p.status

        o['permalink'] = "/pin/%d/" % p.id
        o['resource_uri'] = "/pin/api/post/%d/" % p.id

        if cur_user_id:
            o['like_with_user'] = Likes.user_in_likers(post_id=p.id,
                                                       user_id=cur_user_id)

        if not thumb_size:
            thumb_size = "236"

        net_quality = "normal"
        if r:
            net_quality = str(r.GET.get('net_quality', "normal"))

        o_image = p.image

        # imo = get_thumb(o_image, thumb_size, settings.API_THUMB_QUALITY)
        try:
            if net_quality == "normal":
                imo = p.get_image_500(api=True)
            elif net_quality == "fast":
                imo = p.get_image_500(api=True)
            else:
                imo = p.get_image_236(api=True)
        except Exception, e:
            # print str(e), "166"
            continue

        if imo:
            o['thumbnail'] = imo['url']
            o['hw'] = imo['hw']
        else:
            # print "we dont have imo", p.id, o_image, imo
            continue

        o['category'] = Category.get_json(cat_id=p.category_id)
        objects_list.append(o)

    # cache.set(list_cache_str, objects_list, 600)

    return objects_list


def get_list_post(pl, from_model='latest'):
    arp = []
    pl_str = 'p2_'.join(pl)
    cache_pl = md5(pl_str).hexdigest()
    #print cache_stream_str, cache_stream_name

    posts = cache.get(cache_pl)
    if posts:
        # print "get post fro mcaches"
        return posts

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS2).get(id=pll))
            # print arp
        except Exception, e:
            # print str(e), 'line 182', pll
            r_server.lrem(from_model, str(pll))

    posts = arp
    cache.set(cache_pl, posts, 3600)
    return posts


def post_item(request, item_id):
    thumb_size = "500"

    cache_pi_str = "cpost_item_%s_%s" % (item_id, thumb_size)
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
    log_act("wisgoon.api.post.all.count")
    #print "we are in post"
    data = {}
    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    category_ids = []
    filters = {}
    cur_user = None
    filters.update(dict(status=Post.APPROVED))
    before = request.GET.get('before', None)
    category_id = request.GET.get('category_id', None)
    popular = request.GET.get('popular', None)
    user_id = request.GET.get('user_id', None)

    if before:
        sort_by = ['-timestamp']
    else:
        sort_by = ['-is_ads', '-timestamp']

    token = request.GET.get('token', '')
    if token:
        log_act("wisgoon.api.post.registered.count")
        cur_user = AuthCache.id_from_token(token=token)
    else:
        log_act("wisgoon.api.post.unregistered.count")

    if category_id:
        log_act("wisgoon.api.post.category.count")

        category_ids = category_id.replace(',', ' ').split(' ')
        filters.update(dict(category_id__in=category_ids))

    if before:
        filters.update(dict(id__lt=before))

    if user_id:
        log_act("wisgoon.api.post.users.count")
        if cur_user:
            if Block.objects.filter(user_id=user_id, blocked_id=cur_user).count():
                return HttpResponse('Blocked')

        sort_by = ['-timestamp']
        filters.update(dict(user_id=user_id))
        if cur_user:
            # if int(cur_user) == int(user_id):
            filters.pop('status', None)

    if popular:
        sort_by = ['-cnt_like']
        date_from = None

        dt_now = datetime.datetime.now()
        dt_now = dt_now.replace(minute=0, second=0, microsecond=0)

        #dn = datetime.datetime.now()
        if popular == 'month':
            date_from = dt_now - datetime.timedelta(days=30)
        elif popular == 'lastday':
            date_from = dt_now - datetime.timedelta(days=1)
        elif popular == 'lastweek':
            date_from = dt_now - datetime.timedelta(days=7)
        elif popular == 'lasteigth':
            date_from = dt_now - datetime.timedelta(days=1)

        if date_from:
            start_from = time.mktime(date_from.timetuple())
            pop_posts = SearchQuerySet().models(Post)\
                .filter(timestamp_i__gt=int(start_from))\
                .order_by('-cnt_like_i')[0:30]
        else:
            start_from = time.mktime(date_from.timetuple())
            pop_posts = SearchQuerySet().models(Post)\
                .order_by('-cnt_like_i')[0:30]
            # filters.update(dict(timestamp__gt=start_from))

    cache_stream_str = "v21%s_%s" % (str(filters), sort_by)

    cache_stream_name = md5(cache_stream_str).hexdigest()
    #print cache_stream_str, cache_stream_name

    posts = cache.get(cache_stream_name)
    #print cache_stream_str, cache_stream_name, posts

    if popular:
        posts = []
        for p in pop_posts:
            posts.append(p.object)

    elif not category_id and not popular and not user_id:
        if not before:
            before = 0
        pl = Post.latest(pid=before)
        posts = get_list_post(pl, from_model=settings.STREAM_LATEST)

    elif category_id and len(category_ids) == 1:
        if not before:
            before = 0

        pl = Post.latest(pid=before, cat_id=category_id)
        from_model = "%s_%s" % (settings.STREAM_LATEST_CAT, category_id)
        posts = get_list_post(pl, from_model=from_model)

    elif before:
        if not posts:
            posts = Post.objects\
                .only(*Post.NEED_KEYS2)\
                .filter(**filters).order_by(*sort_by)[:10]

            cache.set(cache_stream_name, posts, 86400)
    else:
        posts = Post.objects\
            .only(*Post.NEED_KEYS2)\
            .filter(**filters).order_by(*sort_by)[:10]
        # if not user_id and not category_id:
        #     # hot_post = Post.get_hot(values=True)
        #     hot_post = Post.objects\
        #         .values(*Post.NEED_KEYS)\
        #         .filter(id=2416517)
        #     if hot_post:
        #         posts = list(hot_post) + list(posts)

    if not user_id and not before:
        hot_post = None

        if cur_user:
            viewer_id = str(cur_user)
        else:
            viewer_id = str(get_user_ip(request))

        ad = Ads.get_ad(user_id=viewer_id)
        if ad:
            hot_post = int(ad.post)
        if hot_post:
            exists_posts = False
            for ppp in posts:
                if ppp.id == hot_post:
                    exists_posts = True
                    break

            if not exists_posts:
                hot_post = Post.objects\
                    .only(*Post.NEED_KEYS2)\
                    .filter(id=hot_post)
                posts = list(hot_post) + list(posts)

        if not hot_post:
            fixed_post = get_fixed_ads()
            if fixed_post:
                fixed_post = Post.objects\
                    .only(*Post.NEED_KEYS2)\
                    .filter(id=fixed_post)
                posts = list(fixed_post) + list(posts)

    thumb_size = int(request.GET.get('thumb_size', "236"))

    #print "thumb_size", thumb_size
    if thumb_size > 400:
        thumb_size = 500
    else:
        thumb_size = "236"

    #cache.set(cache_stream_name, posts, cache_ttl)

    data['objects'] = get_objects_list(posts,
                                       cur_user_id=cur_user,
                                       thumb_size=thumb_size,
                                       r=request)
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def post_details(request, post_id):
    #print "we are in post"
    data = {}
    cur_user = None

    token = request.GET.get('token', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    posts = Post.objects\
        .only(*Post.NEED_KEYS2)\
        .filter(id=post_id)

    thumb_size = int(request.GET.get('thumb_size', "236"))
    if thumb_size > 400:
        thumb_size = 500
    else:
        thumb_size = "236"

    #cache.set(cache_stream_name, posts, cache_ttl)

    data['objects'] = get_objects_list(posts,
                                       cur_user_id=cur_user,
                                       thumb_size=thumb_size)
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def friends_post(request):
    log_act("wisgoon.api.post.friends_post.count")
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    next = {
        'url': "/api/post/friends_post/?limit=%s&offset=%s" % (
            limit, offset + limit),
    }

    data = {}
    data['meta'] = {'limit': 10,
                    'next': next['url'],
                    'offset': offset,
                    'previous': '',
                    'total_count': 1000}

    cur_user = None
    before = request.GET.get('before', None)

    token = request.GET.get('token', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)
    else:
        raise Http404

    if before:
        # s = Stream.objects.get(user=cur_user, post_id=before)
        # stream = Stream.objects.filter(user=cur_user, date__lt=s.date)\
            # .order_by('-date')[offset:offset + limit]
        idis = Post.user_stream_latest(user_id=cur_user, pid=before)
    else:
        # stream = Stream.objects.filter(user=cur_user)\
            # .order_by('-date')[offset:offset + limit]
        idis = Post.user_stream_latest(user_id=cur_user)

    # print "idis is:", idis

    # idis = []
    # for p in stream:
        # idis.append(int(p.post_id))

    posts = Post.objects\
        .only(*Post.NEED_KEYS2)\
        .filter(id__in=idis).order_by('-id')[:limit]

    thumb_size = request.GET.get('thumb_size', "100x100")

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       thumb_size=thumb_size, r=request)

    #data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def likes(request):
    log_act("wisgoon.api.post.likes.count")
    post_id = request.GET.get('post_id', None)
    offset = int(request.GET.get('offset', 0))
    #limit = int(request.GET.get('limit', 20))
    limit = 20

    cache_stream_str = "wislikes2_1_%s_%s_%s" % (str(post_id), str(offset), str(limit))
    cache_stream_name = md5(cache_stream_str).hexdigest()

    # post_likes = cache.get(cache_stream_name)
    # if post_likes:
    #     return HttpResponse(post_likes)

    next = {
        'url': "/pin/api/like/likes/?limit=%s&offset=%s" % (
            limit, offset + limit),
    }

    data = {}
    data['meta'] = {'limit': 20,
                    'next': next['url'],
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    objects_list = []
    filters = {}

    if post_id:
        filters.update(dict(post_id=post_id))
    else:
        return HttpResponse('fault')

    # cache_stream_str = "wislikes_%s_%s_%s" % (str(filters),
    #                                           str(offset), str(limit))

    # cache_stream_name = md5(cache_stream_str).hexdigest()
    #print cache_stream_str, cache_stream_name

    # post_likes = cache.get(cache_stream_name)
    # if not post_likes:
    from models_redis import LikesRedis
    post_likes = LikesRedis(post_id=post_id).get_likes(offset=offset)
    # post_likes = Likes.objects\
    #     .values('id', 'post_id', 'user_id')\
    #     .filter(post_id=post_id).order_by("id")[offset:offset + limit]
        # if len(post_likes) == limit:
        #     #print "store likes in cache"
        #     cache.set(cache_stream_name, post_likes, 86400)

    for p in post_likes:
        p = int(p)
        o = {}
        o['post_id'] = int(post_id)

        o['user_avatar'] = get_avatar(p, size=100)
        o['user_name'] = AuthCache.get_username(user_id=p)

        o['user_url'] = int(p)
        o['resource_uri'] = "/pin/api/like/likes/%d/" % p

        objects_list.append(o)

    #cache.set(cache_stream_name, posts, cache_ttl)

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    # if len(post_likes) == limit:
    #     cache.set(cache_stream_name, json_data, 86400)
    return HttpResponse(json_data)


def notif(request):
    log_act("wisgoon.api.notif.count")
    data = {}
    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    objects_list = []
    filters = {}
    cur_user = None
    filters.update(dict(status=Post.APPROVED))

    token = request.GET.get('api_key', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    notifs = Notif.objects.filter(owner=cur_user).order_by('-date')[:50]

    Notif.objects.filter(owner=cur_user, seen=False).update(set__seen=True)

    Notif.objects.filter(owner=1).order_by('-date')[100:].delete()

    for p in notifs:
        try:
            cur_p = Post.objects.only(*Post.NEED_KEYS2).get(id=p.post)
            if cur_p.is_pending():
                continue
        except Post.DoesNotExist:
            continue
        o = {}
        o['id'] = cur_p.id
        o['text'] = cur_p.text
        o['cnt_comment'] = 0 if cur_p.cnt_comment == -1 else \
            cur_p.cnt_comment
        o['image'] = cur_p.image
        o['date'] = "2014-05-28T20:22:14"

        # av = AuthCache.avatar(user_id=cur_p.user_id)
        #o['user_avatar'] = AuthCache.avatar(user_id=cur_p.user_id)[1:]
        #o['user_name'] = AuthCache.get_username(user_id=cur_p.user_id)

        o['post'] = "/pin/api1/post/879/"
        o['post_id'] = cur_p.id
        o['post_owner_avatar'] = AuthCache.avatar(user_id=cur_p.user_id)[1:]
        o['post_owner_id'] = cur_p.user_id
        o['post_owner_user_name'] = AuthCache.get_username(
            user_id=cur_p.user_id)

        o['user'] = cur_p.user_id
        o['type'] = p['type']
        o['like'] = cur_p.cnt_like
        o['timestamp'] = cur_p.timestamp
        o['url'] = ""
        o['likers'] = None
        o['like_with_user'] = False

        #o['resource_uri'] = "/pin/api/notif/notify/%d/" % cur_p.id
        o['resource_uri'] = "/pin/api/post/%d/" % cur_p.id
        o['permalink'] = "/pin/%d/" % cur_p.id

        if cur_user:
            o['like_with_user'] = Likes.user_in_likers(post_id=cur_p.id,
                                                       user_id=cur_user)

        #thumb_size = request.GET.get('thumb_size', "100x100")
        thumb_size = "236"
        thumb_quality = 99

        o_image = cur_p.image

        imo = cur_p.get_image_500(api=True)

        if imo:
            o['thumbnail'] = imo['url']
            o['hw'] = imo['hw']

        o['category'] = Category.get_json(cat_id=cur_p.category_id)

        ar = []
        for ac in p.last_actors():
            ar.append([
                ac,
                AuthCache.get_username(ac),
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
        'url': "/pin/api/following/%s/?limit=%s&offset=%s" % (
            user_id, limit, offset + limit),
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

    fq = Follow.objects.filter(follower_id=user_id)[offset:offset + limit]
    for fol in fq:
        o = {}
        o['user_id'] = fol.following_id
        o['user_avatar'] = get_avatar(fol.following_id, size=100)
        o['user_name'] = AuthCache.get_username(fol.following_id)

        if cur_user:
            o['follow_by_user'] = Follow.objects\
                .filter(follower_id=cur_user, following_id=fol.following_id)\
                .exists()
        else:
            o['follow_by_user'] = False

        objects_list.append(o)

    data['objects'] = objects_list

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def comments(request):
    log_act("wisgoon.api.comments.count")
    data = {}

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    object_pk = int(request.GET.get('object_pk', 0))

    comment_cache_name = "com_%d" % object_pk
    cc = cache.get(comment_cache_name)
    pc = "%d-%d" % (offset, limit)
    if not cc:
        print "empty cache"
        cc = {}
    elif pc in cc:
        print "cache hooooray!!!"
        return HttpResponse(cc[pc], content_type="application/json")

    next = {
        'url': "/pin/api/com/comments/?limit=%s&offset=%s&object_pk=%s" % (
            limit, offset + limit, object_pk)
    }

    data['meta'] = {'limit': limit,
                    'next': next['url'],
                    'offset': offset,
                    'previous': '',
                    'total_count': 1000}

    objects_list = []

    cq = Comments.objects.filter(object_pk_id=object_pk, is_public=True)\
        .order_by('-id')[offset:offset + limit]
    for com in cq:
        o = {}
        o['id'] = com.id
        o['object_pk'] = com.object_pk_id
        o['score'] = com.score

        com_date = com.submit_date.astimezone(timezone('Asia/Tehran'))
        com_date = com_date.strftime('%Y-%m-%dT%H:%M:%S')

        o['submit_date'] = com_date
        o['comment'] = com.comment
        o['user_url'] = com.user_id
        o['user_avatar'] = get_avatar(com.user_id, size=100)
        o['user_name'] = AuthCache.get_username(com.user_id)
        o['resource_uri'] = "/pin/api/com/comments/%d/" %com.id

        objects_list.append(o)

    data['objects'] = objects_list

    json_data = json.dumps(data, cls=MyEncoder)

    pc = "%d-%d" % (offset, limit)
    cc[pc] = json_data
    cache.set(comment_cache_name, cc, 86400)
    return HttpResponse(json_data, content_type="application/json")


def follower(request, user_id=1):
    data = {}
    cur_user = None
    follow_cnt = Follow.objects.filter(following_id=user_id).count()

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    next = {
        'url': "/pin/api/followers/%s/?limit=%s&offset=%s" % (
            user_id, limit, offset + limit),
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

    fq = Follow.objects.filter(following_id=user_id)[offset:offset + limit]
    for fol in fq:
        o = {}
        o['user_id'] = fol.follower_id
        o['user_avatar'] = get_avatar(fol.follower_id, size=100)
        o['user_name'] = AuthCache.get_username(fol.follower_id)

        if cur_user:
            o['follow_by_user'] = Follow.objects\
                .filter(follower_id=cur_user, following_id=fol.follower_id)\
                .exists()
        else:
            o['follow_by_user'] = False

        objects_list.append(o)

    data['objects'] = objects_list

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def search(request):
    log_act("wisgoon.api.search.count")
    cur_user = None
    limit = request.GET.get('limit', 20)
    start = request.GET.get('start', 0)

    data = {}
    import pysolr
    solr = pysolr.Solr('http://79.127.125.146:8080/solr/wisgoon_user', timeout=10)
    query = request.GET.get('q', '')
    if query:
        fq = 'username_s:*%s* name_s:*%s*' % (query, query)
        try:
            results = solr.search("*:*", fq=fq, rows=limit, start=start,
                              sort="score_i desc")
        except:
            results = []

        token = request.GET.get('token', '')
        if token:
            cur_user = AuthCache.id_from_token(token=token)

        data['objects'] = []
        for r in results:
            o = {}
            o['id'] = r['id']
            o['avatar'] = get_avatar(r['id'], 100)
            o['username'] = r['username_s']
            try:
                o['name'] = r['name_s']
            except:
                o['name'] = ""

            if cur_user:
                o['follow_by_user'] = Follow\
                    .get_follow_status(follower=cur_user, following=r['id'])
            else:
                o['follow_by_user'] = False

            data['objects'].append(o)

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def search2(request):
    from user_profile.models import Profile
    ROW_PER_PAGE = 20
    cur_user = None
    limit = request.GET.get('limit', 20)
    start = request.GET.get('start', 0)

    query = request.GET.get('q', '')
    offset = int(request.GET.get('offset', 0))
    results = SearchQuerySet().models(Profile)\
        .filter(content__contains=query)[offset:offset + 1 * ROW_PER_PAGE]

    data = {}
    # import pysolr
    # solr = pysolr.Solr('http://localhost:8983/solr/wisgoon_user', timeout=10)
    # query = request.GET.get('q', '')
    if query:
        # fq = 'username_s:*%s* name_s:*%s*' % (query, query)
        # results = solr.search("*:*", fq=fq, rows=limit, start=start,
        #                       sort="score_i desc")

        token = request.GET.get('token', '')
        if token:
            cur_user = AuthCache.id_from_token(token=token)

        data['objects'] = []
        for r in results:
            r = r.object
            o = {}
            o['id'] = r['id']
            o['avatar'] = get_avatar(r['id'], 100)
            o['username'] = r['username_s']
            try:
                o['name'] = r['name_s']
            except:
                o['name'] = ""

            if cur_user:
                o['follow_by_user'] = Follow\
                    .get_follow_status(follower=cur_user, following=r['id'])
            else:
                o['follow_by_user'] = False

            data['objects'].append(o)

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def hashtag_top(request):
    tags = []
    sqs = SearchQuerySet().models(Post).facet('tags', mincount=10, limit=100)
    # print sqs.facet_counts()
    if sqs:
        tags = [t for t in sqs.facet_counts()['fields']['tags']]

    # print tags

    data = {}
    o = []
    for t in tags:
        dt = {
            "tag": t[0],
            "count": t[1]
        }
        o.append(dt)
        # print dt
    data['objects'] = o

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)

def hashtag(request):
    ROW_PER_PAGE = 20
    cur_user = None

    query = request.GET.get('q', '')
    query = query.replace('#', '')
    offset = int(request.GET.get('offset', 0))
    results = SearchQuerySet().models(Post)\
        .filter(tags=query)\
        .order_by('-timestamp_i')[offset:offset + 1 * ROW_PER_PAGE]

    data = {}

    if query:
        token = request.GET.get('token', '')
        if token:
            cur_user = AuthCache.id_from_token(token=token)
        posts = []
        for p in results:
            try:
                pp = Post.objects\
                    .only(*Post.NEED_KEYS2)\
                    .get(id=p.object.id)

                posts.append(pp)
            except:
                pass

        thumb_size = request.GET.get('thumb_size', "100x100")

        data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       thumb_size=thumb_size, r=request)
        

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)

@csrf_exempt
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email='info@wisgoon.com',
                   current_app=None,
                   extra_context=None):

    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
            }
            if is_admin_site:
                opts = dict(opts, domain_override=request.get_host())
            form.save(**opts)
            return HttpResponse('email sent')
    else:
        form = password_reset_form()
    context = {
        'form': form,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context,
                            current_app=current_app)


@csrf_exempt
def change_password(request):
    token = request.GET.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        raise Http404

    try:
        new_pass = request.POST.get('new_pass', '')
        if new_pass:
            user.set_password(new_pass)
            user.save()
            return HttpResponse('password changed')

        return HttpResponse('error in parameters')

    except Exception, e:
        print str(e)

    return HttpResponse('error in change password')


def comment_delete(request, id):
    user = None
    token = request.GET.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        raise Http404

    try:
        comment = Comments.objects.get(pk=id)
    except Comments.DoesNotExist:
        return HttpResponse('Comment Does Not Exist', status=404)

    post_owner = int(comment.object_pk.user_id)
    comment_owner = int(comment.user_id)
    user_id = int(user.id)

    if post_owner == user_id:
        # post owner like to remove a comment
        comment.delete()
        return HttpResponse(1)

    if comment_owner == user_id:
        # comment owner like to remove a comment
        comment.delete()
        return HttpResponse(1)

    # if user.is_superuser:
    #     print "admin like to remove a comment"
    #     comment.delete()
    #     return HttpResponse(1)
    
    return HttpResponse(0)


def block_user(request, user_id):
    user = None
    token = request.GET.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        raise Http404

    Block.block_user(user_id=user.id, blocked_id=user_id)
    return HttpResponse('1')


def unblock_user(request, user_id):
    user = None
    token = request.GET.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        raise Http404

    Block.unblock_user(user_id=user.id, blocked_id=user_id)
    return HttpResponse('1')
