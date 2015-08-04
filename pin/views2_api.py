# -*- coding: utf-8 -*-

try:
    import simplejson as json
except ImportError:
    import json

import urllib2

import datetime
import time
import redis
from hashlib import md5
from pytz import timezone

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from sorl.thumbnail import get_thumbnail
from tastypie.models import ApiKey

from pin.tools import AuthCache, get_user_ip, log_act
from pin.models import Post, Category, Likes, Follow, Comments, Block,\
    Packages, Ad, Bills2, PhoneData, Log
from pin.model_mongo import Notif, UserLocation, NotifCount
from pin.tasks import send_clear_notif
from pin.cacheLayer import UserNameCache

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


def check_auth(request):
    token = request.GET.get('token', '')
    if not token:
        return False

    try:
        # api = ApiKey.objects.get(key=token)
        # user = api.user
        user = AuthCache.user_from_token(token)
        if not user:
            return False
        user._ip = get_user_ip(request)

        if not user.is_active:
            return False
        else:
            return user
    except ApiKey.DoesNotExist:
        return False

    return False


def notif_count(request):
    cur_user_id = None
    token = request.GET.get('token', '')
    if token:
        cur_user_id = AuthCache.id_from_token(token=token)

    if not cur_user_id:
        return HttpResponseForbidden('Token problem')

    try:
        notify = NotifCount.objects.filter(owner=cur_user_id).first().unread
    except Exception, e:
        print str(e)
        notify = 0

    return HttpResponse(notify, content_type="application/json")


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

        try:
            if p.is_pending():
                continue
        except Post.DoesNotExist:
            continue
        o = {}
        o['id'] = p.id
        o['text'] = p.text
        o['cnt_comment'] = 0 if p.cnt_comment == -1 else p.cnt_comment
        o['image'] = p.image

        o['user_avatar'] = get_avatar(p.user_id, size=100)
        # o['user_name'] = AuthCache.get_username(user_id=p.user_id)
        o['user_name'] = UserNameCache.get_user_name(user_id=p.user_id)

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

        try:
            o['is_ad'] = False  # p.is_ad
        except Exception, e:
            # print str(e)
            o['is_ad'] = False

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

        # o_image = p.image
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

    posts = cache.get(cache_pl)
    if posts:
        # print "get post fro mcaches"
        return posts

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS2).get(id=pll))
            # print arp
        except Exception:
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
    return HttpResponse(json_data, content_type="application/json")


def post(request):
    log_act("wisgoon.api.post.all.count")
    data = {}
    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    category_ids = []
    filters = {}
    cur_user = None
    # filters.update(dict(status=Post.APPROVED))
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
            if Block.objects.filter(user_id=user_id, blocked_id=cur_user)\
                    .count():
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

    posts = cache.get(cache_stream_name)

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
    if not user_id and not category_id:
        hot_post = None

        if cur_user:
            viewer_id = str(cur_user)
        else:
            viewer_id = str(get_user_ip(request))

        ad = Ad.get_ad(user_id=viewer_id)
        if ad:
            hot_post = int(ad.post_id)
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
                for h in hot_post:
                    h.is_ad = True
                posts = list(hot_post) + list(posts)

        # if not hot_post:
        #     fixed_post = get_fixed_ads()
        #     if fixed_post:
        #         fixed_post = Post.objects\
        #             .only(*Post.NEED_KEYS2)\
        #             .filter(id=fixed_post)
        #         posts = list(fixed_post) + list(posts)

    thumb_size = int(request.GET.get('thumb_size', "236"))

    if thumb_size > 400:
        thumb_size = 500
    else:
        thumb_size = "236"

    data['objects'] = get_objects_list(posts,
                                       cur_user_id=cur_user,
                                       thumb_size=thumb_size,
                                       r=request)
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def post_details(request, post_id):
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

    data['objects'] = get_objects_list(posts,
                                       cur_user_id=cur_user,
                                       thumb_size=thumb_size)
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


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

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def likes(request):
    log_act("wisgoon.api.post.likes.count")
    post_id = request.GET.get('post_id', None)
    offset = int(request.GET.get('offset', 0))
    limit = 20

    # cache_stream_str = "wislikes2_1_%s_%s_%s" % (str(post_id), str(offset),
    #    str(limit))
    # cache_stream_name = md5(cache_stream_str).hexdigest()

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

    from models_redis import LikesRedis
    post_likes = LikesRedis(post_id=post_id).get_likes(offset=offset)

    for p in post_likes:
        p = int(p)
        o = {}
        o['post_id'] = int(post_id)

        o['user_avatar'] = get_avatar(p, size=100)
        # o['user_name'] = AuthCache.get_username(user_id=p)
        o['user_name'] = UserNameCache.get_user_name(user_id=p)

        o['user_url'] = int(p)
        o['resource_uri'] = "/pin/api/like/likes/%d/" % p

        objects_list.append(o)

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    # if len(post_likes) == limit:
    #     cache.set(cache_stream_name, json_data, 86400)
    return HttpResponse(json_data, content_type="application/json")


def notif(request):
    log_act("wisgoon.api.notif.count")

    data = {}
    objects_list = []
    filters = {}
    cur_user = None

    # from my_notif import NotifCas
    # for n in NotifCas.objects.all():
    #     print n[0]

    offset = int(request.GET.get('offset', 0))
    limit = 40
    token = request.GET.get('api_key', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)
    else:
        return HttpResponse("token problem")

    if not cur_user:
        return HttpResponse("problem", cur_user)

    notif_cache_key = "notif_v112_%d" % (int(cur_user))
    c_data = cache.get(notif_cache_key)
    if c_data:
        pass
        # print "get from cache", notif_cache_key
        # return HttpResponse(c_data, content_type="application/json")

    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    # filters.update(dict(status=Post.APPROVED))

    notifs = Notif.objects.filter(owner=cur_user).order_by('-date')[offset:offset + limit]

    NotifCount.objects.filter(owner=cur_user).update(set__unread=0)
    # send_clear_notif(user_id=cur_user)

    # Notif.objects.filter(owner=1).order_by('-date')[100:].delete()

    for p in notifs:
        if p.type == 4:

            class CurP:
                def get_image_500(self, api):
                    return self.post_image

            cur_p = CurP()
            cur_p.id = p.post
            cur_p.text = ""
            cur_p.cnt_comment = 0
            cur_p.post_image = p.post_image
            cur_p.post_image['url'] = cur_p.post_image['url']\
                .split("media/")[1]
            cur_p.image = p.post_image['url']
            cur_p.user_id = p.owner
            cur_p.cnt_like = 0
            cur_p.timestamp = int(time.time())
            cur_p.category_id = 1
        elif p.type == 10:

            class CurP:
                def get_image_500(self, api):
                    return self.post_image

            cur_p = CurP()
            cur_p.id = p.owner
            cur_p.text = ""
            cur_p.cnt_comment = 0
            owner = p.owner
            cur_p.image = AuthCache.avatar(user_id=p.owner)\
                .split("media/")[1]
            cur_p.user_id = p.owner
            cur_p.cnt_like = 0
            cur_p.timestamp = int(time.time())
            cur_p.category_id = 1
            cur_p.owner = p.owner
            cur_p.last_actor = p.last_actor
        else:
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

        o['post'] = "/pin/api1/post/879/"
        o['post_id'] = cur_p.id
        o['post_owner_avatar'] = AuthCache.avatar(user_id=cur_p.user_id)[1:]
        o['post_owner_id'] = cur_p.user_id
        # o['post_owner_user_name'] = AuthCache.get_username(
        #     user_id=cur_p.user_id)

        o['post_owner_user_name'] = UserNameCache.get_user_name(
            user_id=cur_p.user_id)

        o['user'] = cur_p.user_id
        o['type'] = p['type']
        o['like'] = cur_p.cnt_like
        o['timestamp'] = cur_p.timestamp
        o['url'] = ""
        o['likers'] = None
        o['like_with_user'] = False

        if p.type == 10:
            o['resource_uri'] = "/pin/api/post/%d/" % cur_p.owner
        else:
            o['resource_uri'] = "/pin/api/post/%d/" % cur_p.id

        if p.type == 10:
            o['permalink'] = "/profile/%d/" % cur_p.last_actor
        else:
            o['permalink'] = "/pin/%d/" % cur_p.id

        if cur_user:
            o['like_with_user'] = Likes.user_in_likers(post_id=cur_p.id,
                                                       user_id=cur_user)

        if p.type == 10:
            imo = cur_p.image
        else:
            imo = cur_p.get_image_500(api=True)

        if p.type == 10:
            o['thumbnail'] = imo
            o['hw'] = "100x100"
        elif imo:
            o['thumbnail'] = imo['url']
            o['hw'] = imo['hw']

        o['category'] = Category.get_json(cat_id=cur_p.category_id)

        ar = []
        if p.type == 10:
            # p['actors'] = [get_avatar(p.last_actor, size=100)]
            ar.append([
                    p.last_actor,
                    AuthCache.get_username(p.last_actor),
                    get_avatar(p.last_actor, size=100)
                ])
        else:
            
            for ac in [p.last_actor]:
                ar.append([
                    ac,
                    AuthCache.get_username(ac),
                    get_avatar(ac, size=100)
                ])
                break

        o['actors'] = ar

        from collections import OrderedDict
        o = OrderedDict(sorted(o.items(), key=lambda o: o[0]))

        objects_list.append(o)

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    cache.set(notif_cache_key, json_data, 86400)
    return HttpResponse(json_data, content_type="application/json")


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
        o['user_name'] = UserNameCache.get_user_name(fol.following_id)

        if cur_user:
            o['follow_by_user'] = Follow.objects\
                .filter(follower_id=cur_user, following_id=fol.following_id)\
                .exists()
        else:
            o['follow_by_user'] = False

        objects_list.append(o)

    data['objects'] = objects_list

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


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
        # print "empty cache"
        cc = {}
    elif pc in cc:
        # print "cache hooooray!!!"
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

    cq = Comments.objects.filter(object_pk_id=object_pk)\
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
        # o['user_name'] = AuthCache.get_username(com.user_id)
        o['user_name'] = com.get_username()
        o['resource_uri'] = "/pin/api/com/comments/%d/" % com.id

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
        o['user_name'] = UserNameCache.get_user_name(fol.follower_id)

        if cur_user:
            o['follow_by_user'] = Follow.objects\
                .filter(follower_id=cur_user, following_id=fol.follower_id)\
                .exists()
        else:
            o['follow_by_user'] = False

        objects_list.append(o)

    data['objects'] = objects_list

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def search(request):
    log_act("wisgoon.api.search.count")
    cur_user = None
    row_per_page = 10

    offset = int(request.GET.get('offset', 0))

    data = {}

    query = request.GET.get('q', None)

    if not query:
        json_data = json.dumps(data, cls=MyEncoder)
        return HttpResponse(json_data, content_type="application/json")

    if query:
        from user_profile.models import Profile
        from haystack.query import SQ
        from haystack.query import Raw

        words = query.split()

        sq = SQ()
        for w in words:
            sq.add(SQ(text__contains=Raw("%s*" % w)), SQ.OR)
            sq.add(SQ(text__contains=Raw(w)), SQ.OR)
        # sqs = SearchQuerySet().filter(sqs)

        # results = SearchQuerySet().models(Profile)\
        #     .filter(SQ(text__contains=Raw(query2)))[offset:offset + 1 * row_per_page]

        results = SearchQuerySet().models(Profile)\
            .filter(sq)[offset:offset + 1 * row_per_page]

        token = request.GET.get('token', '')
        if token:
            cur_user = AuthCache.id_from_token(token=token)

        data['objects'] = []
        for r in results:
            o = {}
            r = r.object
            o['id'] = r.user_id
            o['avatar'] = get_avatar(r.user_id, 100)
            o['username'] = r.user.username
            try:
                o['name'] = r.name
            except:
                o['name'] = ""

            if cur_user:
                o['follow_by_user'] = Follow\
                    .get_follow_status(follower=cur_user, following=r.user_id)
            else:
                o['follow_by_user'] = False

            data['objects'].append(o)

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def search2(request):
    from user_profile.models import Profile
    row_per_page = 20
    cur_user = None

    query = request.GET.get('q', '')
    offset = int(request.GET.get('offset', 0))
    results = SearchQuerySet().models(Profile)\
        .filter(content__contains=query)[offset:offset + 1 * row_per_page]

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
    return HttpResponse(json_data, content_type="application/json")


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
    return HttpResponse(json_data, content_type="application/json")


def hashtag(request):
    log_act("wisgoon.api.post.hashtag.count")
    row_per_page = 20
    cur_user = None

    query = request.GET.get('q', '')
    query = query.replace('#', '')
    offset = int(request.GET.get('offset', 0))

    data = {}

    if query:
        results = SearchQuerySet().models(Post)\
            .filter(tags=query)\
            .order_by('-timestamp_i')[offset:offset + 1 * row_per_page]
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
    return HttpResponse(json_data, content_type="application/json")


def search_posts(request):
    log_act("wisgoon.api.post.search_posts.count")
    row_per_page = 20
    cur_user = None

    query = request.GET.get('q', '')
    offset = int(request.GET.get('offset', 0))

    data = {}

    if query:
        results = SearchQuerySet().models(Post)\
            .filter(content__contains=query)[offset:offset + 1 * row_per_page]
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
    return HttpResponse(json_data, content_type="application/json")


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


PACKS = {
    "wisgoon_pack_1": {
        "price": 650,
        "wis": 500
    },
    "wisgoon_pack_2": {
        "price": 1300,
        "wis": 1000
    },
    "wisgoon_pack_3": {
        "price": 2600,
        "wis": 2000
    },
    "wisgoon_pack_4": {
        "price": 6500,
        "wis": 5000
    },
}


@cache_page(60 * 15)
def packages(request):
    # return HttpResponse("hello")

    data = {
        "objects": []
    }

    for p in Packages.objects.all():
        o = {
            "name": p.name,
            "title": p.title,
            "price": p.price,
            "wis": p.wis,
            "icon": str(p.icon.url)
        }
        data['objects'].append(o)

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


@cache_page(60 * 15)
def packages_old(request):
    # return HttpResponse("hello")

    data = {
        "objects": []
    }

    o = {
        "name": "update",
        "title": u"لطفا نسخه ی جدید را نصب کنید - 5.0.3",
        "price": 0,
        "wis": 0,
        "icon": "/media/packages/ic_credit_gold.png"
    }
    data['objects'].append(o)

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def promotion_prices(request):
    data = {
        "objects": [
            {
                "price": 500,
                "visitors": 1000
            },
            {
                "price": 1000,
                "visitors": 3000
            },
            {
                "price": 2000,
                "visitors": 6000,
            },
            {
                "price": 5000,
                "visitors": 15000
            }
        ]
    }
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def user_credit(request):
    user = None
    token = request.GET.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        raise Http404

    data = {
        "credit": user.profile.credit,
    }

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def inc_credit(request):

    user = None
    token = request.GET.get('token', '')
    price = int(request.GET.get('price', 0))
    baz_token = request.GET.get("baz_token", "")
    package_name = request.GET.get("package", "")
    if token:
        user = check_auth(request)

    print user, token, baz_token, package_name

    if not user or not token or not baz_token or not package_name:
        return HttpResponse("default values erros", status=404)

    if package_name not in PACKS:
        return HttpResponse("package error", status=404)

    print PACKS[package_name]['price'], price

    if PACKS[package_name]['price'] == price:
        if Bills2.objects.filter(trans_id=str(baz_token), status=Bills2.COMPLETED).count() > 0:
            b = Bills2()
            b.trans_id = str(baz_token)
            b.user = user
            b.amount = PACKS[package_name]['price']
            b.status = Bills2.FAKERY
            b.save()
            return HttpResponse("bazzar token error", status=404)
        else:
            url = "https://pardakht.cafebazaar.ir/api/validate/ir.mohsennavabi.wisgoon/inapp/%s/purchases/%s/?access_token=gtp8TnDCJjqc2ZVBIiat3KpvpmxDsc" % (package_name, baz_token)
            try:
                u = urllib2.urlopen(url).read()
                j = json.loads(u)

                if len(j) == 0:
                    b = Bills2()
                    b.trans_id = str(baz_token)
                    b.user = user
                    b.amount = PACKS[package_name]['price']
                    b.status = Bills2.NOT_VALID
                    b.save()
                    return HttpResponse("ex price error")

                purchase_state = j.get('purchaseState', None)
                if purchase_state is None:
                    raise

                if purchase_state == 0:

                    b = Bills2()
                    b.trans_id = str(baz_token)
                    b.user = user
                    b.amount = PACKS[package_name]['price']
                    b.status = Bills2.COMPLETED
                    b.save()

                    # p = user.profile
                    # p.credit = p.credit + PACKS[package_name]['wis']
                    # p.save()
                    p = user.profile
                    p.inc_credit(amount=PACKS[package_name]['wis'])
                else:
                    b = Bills2()
                    b.trans_id = str(baz_token)
                    b.user = user
                    b.amount = PACKS[package_name]['price']
                    b.status = Bills2.NOT_VALID
                    b.save()
                    return HttpResponse("ex price error")
            except Exception, e:
                b = Bills2()
                b.trans_id = str(baz_token)
                b.user = user
                b.amount = PACKS[package_name]['price']
                b.status = Bills2.VALIDATE_ERROR
                b.save()
                return HttpResponse("ex price error")

            return HttpResponse("success full", content_type="text/html")
    else:
        return HttpResponse("price error")

    return HttpResponse("failed", content_type="text/html")


@csrf_exempt
def save_as_ads(request, post_id):
    try:
        Post.objects.get(id=int(post_id))
    except Exception, Post.DoesNotExist:
        return HttpResponse("error in post id",
                            status=404,
                            content_type="text/html")

    user = None
    token = request.GET.get('token', '')

    if token:
        user = check_auth(request)

    if not user or not token:
        return HttpResponseForbidden("token error")

    profile = user.profile

    if request.method == "POST":
        mode = int(request.POST.get('mode', 0))
        if mode == 0:
            return HttpResponseForbidden("mode error")

        try:
            mode_price = Ad.TYPE_PRICES[mode]
        except KeyError:
            return HttpResponseForbidden("mode error")

        if profile.credit >= int(mode_price):
            try:
                Ad.objects.get(post=int(post_id), ended=False)
                return HttpResponseForbidden(u"این پست قبلا آگهی شده است")
            except Exception, Ad.DoesNotExist:
                # p = bill.user.profile
                profile.dec_credit(amount=int(mode_price))
                Ad.objects.create(user_id=user.id,
                                  post_id=int(post_id),
                                  ads_type=mode,
                                  start=datetime.datetime.now(),
                                  ip_address=get_user_ip(request))
                return HttpResponse(u'مطلب مورد نظر شما با موفقیت آگهی شد.')

        else:
            return HttpResponseForbidden(u"موجودی حساب شما برای آگهی دادن کافی نیست.")

    return HttpResponseForbidden("error in data")


def promoted(request):
    data = {}

    user = None
    token = request.GET.get('token', '')

    if token:
        user = AuthCache.user_from_token(token=token)

    if not user:
        return HttpResponseForbidden("error in token")

    row_per_page = 20
    offset = int(request.GET.get('offset', 0))

    # Norton utility :D
    nu = "/pin/api/promoted/post/?token=%s&offset=%s" % (token, offset + row_per_page)

    data = {
        "meta": {
            "next": nu
        }
    }

    objects = []

    for ad in Ad.objects.filter(Q(owner=user) | Q(user=user)).order_by("-id")[offset:offset + 1 * row_per_page]:
        o = {}
        o['post'] = get_objects_list([ad.post], cur_user_id=user.id, thumb_size=250)
        o['cnt_view'] = ad.get_cnt_view()
        o['user'] = ad.user.id
        o['ended'] = ad.ended
        o['owner'] = ad.owner.id
        # o['cnt_view'] = ad.cnt_view
        o['ads_type'] = ad.ads_type
        o['start'] = str(ad.start)
        o['end'] = str(ad.end)

        objects.append(o)

    data['objects'] = objects

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")

    # return HttpResponse(json.dumps(data))


def get_phone_data(request):
    os = request.GET.get("os", "")
    app_version = request.GET.get("app_version", "")
    google_token = request.GET.get("google_token", "")
    token = request.GET.get("user_wisgoon_token", None)
    imei = request.GET.get("imei", "")
    phone_brand = request.GET.get("phone_brand", "")
    android_version = request.GET.get("android_version", "")
    phone_serial = request.GET.get("phone_serial", "")
    phone_model = request.GET.get("phone_model", "")

    if not token:
        return HttpResponse("not only :D", content_type="text/html")

    if token:
        user = AuthCache.user_from_token(token=token)

    if imei:
        for pdq in PhoneData.objects.filter(imei=imei):
            if not pdq.user.is_active:
                u = User.objects.get(pk=user.id)
                if u.is_active:
                    u.is_active = False
                    u.save()
                    Log.ban_by_imei(actor=user, text=pdq.user.username,
                                    ip_address=get_user_ip(request))

    upd, created = PhoneData.objects.get_or_create(user=user)
    upd.imei = imei
    upd.os = os
    upd.phone_model = phone_model
    upd.phone_serial = phone_serial
    upd.android_version = android_version
    upd.app_version = app_version
    upd.google_token = google_token
    upd.logged_out = False
    upd.save()

    return HttpResponse("accepted", content_type="text/html")


def get_plus_data(request):
    token = request.GET.get("token", None)
    lat = float(request.GET.get("lat", 0))
    lon = float(request.GET.get('lon', 0))
    if lat == 0 and lon == 0:
        return HttpResponse("leave me alone", content_type="text/html")
    if not token:
        return HttpResponse("not only :D", content_type="text/html")

    if token:
        user = AuthCache.user_from_token(token=token)

    ul, created = UserLocation.objects.get_or_create(user=user.id)
    ul.point = [lat, lon]
    ul.save()
    return HttpResponse("accepted", content_type="text/html")


def logout(request):
    token = request.GET.get("token", None)

    if token:
        user = AuthCache.user_from_token(token=token)
        PhoneData.objects.filter(user=user)\
            .update(logged_out=True)

    return HttpResponse("logged out", content_type="text/html")
