# -*- coding: utf-8 -*-
try:
    import simplejson as json
except ImportError:
    import json

import urlparse
import urllib2
import hashlib

import datetime
import time
import redis
from hashlib import md5

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.template.response import TemplateResponse
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt

from sorl.thumbnail import get_thumbnail
from tastypie.models import ApiKey

from pin.tools import AuthCache, get_user_ip, get_new_access_token,\
    get_post_user_cache
from pin.models import Post, Category, Likes, Comments, Block,\
    Ad, Bills2, PhoneData, BannedImei
from pin.model_mongo import UserLocation
from pin.models_redis import NotificationRedis, PostView
from pin.cacheLayer import UserDataCache, CategoryDataCache
from pin.api6.tools import post_item_json, is_system_writable

from haystack.query import SearchQuerySet

from daddy_avatar.templatetags.daddy_avatar import get_avatar

User = get_user_model()
r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        return json.JSONEncoder.default(self, obj)


def check_auth(request):
    token = request.GET.get('token', '')
    if not token:
        return False

    try:
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

    notify = NotificationRedis(user_id=cur_user_id).get_notif_count()
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
        PostView(post_id=int(p.id)).inc_view()
        o['text'] = p.text
        o['cnt_comment'] = 0 if p.cnt_comment == -1 else p.cnt_comment
        o['image'] = p.image

        o['user_avatar'] = get_avatar(p.user_id, size=100)
        o['user_name'] = UserDataCache.get_user_name(user_id=p.user_id)

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
            o['is_ad'] = False
        except Exception, e:
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

        try:
            if net_quality == "normal":
                imo = p.get_image_500(api=True)
            elif net_quality == "fast":
                imo = p.get_image_500(api=True)
            else:
                imo = p.get_image_236(api=True)
        except Exception, e:
            continue

        if imo:
            o['thumbnail'] = imo['url']
            o['hw'] = imo['hw']
        else:
            continue
        o['category'] = CategoryDataCache\
            .get_cat_json(category_id=p.category_id)
        objects_list.append(o)

    return objects_list


def fix_url(url):
    path = urlparse.urlparse(url).path
    path = path.replace('/media/', '')
    return path


def get_objects_list2(posts, cur_user_id, thumb_size, r=None):
    objects_list = []
    for p in posts:
        if not p:
            continue

        o = {}
        try:
            o['id'] = p['id']
        except TypeError, e:
            print str(e), p
            continue
        o['text'] = p['text']
        o['cnt_comment'] = 0 if p['cnt_comment'] == -1 else p['cnt_comment']
        try:
            o['image'] = fix_url(p['images']['original']['url'])
        except KeyError:
            print "post original url DoesNotExist", p
            continue

        o['user_avatar'] = get_avatar(p['user']['id'], size=100)
        o['user_name'] = UserDataCache.get_user_name(user_id=p['user']['id'])

        o['timestamp'] = p['timestamp']

        o['user'] = p['user']['id']
        o['url'] = p['url']
        o['like'] = p['cnt_like']
        o['likers'] = None
        o['like_with_user'] = False
        o['status'] = p['status']

        o['is_ad'] = False

        o['permalink'] = "/pin/%d/" % p['id']
        o['resource_uri'] = "/pin/api/post/%d/" % p['id']

        if cur_user_id:
            o['like_with_user'] = Likes.user_in_likers(post_id=p['id'],
                                                       user_id=cur_user_id)

        if not thumb_size:
            thumb_size = "236"

        net_quality = "normal"
        if r:
            net_quality = str(r.GET.get('net_quality', "normal"))

        try:
            if net_quality in ["normal", "fast"]:
                imo = p['images']['low_resolution']
            else:
                imo = p['images']['thumbnail']
        except Exception:
            continue

        if imo:
            o['thumbnail'] = fix_url(imo['url'])
            o['hw'] = "{}x{}".format(imo['height'], imo['width'])
        else:
            continue
        o['category'] = CategoryDataCache\
            .get_cat_json(category_id=p['category']['id'])
        objects_list.append(o)

    return objects_list


def get_list_post(pl, from_model='latest'):
    arp = []
    pl_str = 'p2_'.join(pl)
    cache_pl = md5(pl_str).hexdigest()

    posts = cache.get(cache_pl)
    if posts:
        return posts

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS2).get(id=pll))
        except Exception:
            r_server.lrem(from_model, str(pll))

    posts = arp
    cache.set(cache_pl, posts, 3600)
    return posts


def get_list_post2(pl, from_model='latest', cur_user_id=None):
    arp = []

    for pll in pl:
        op = post_item_json(pll, cur_user_id=cur_user_id)
        if op:
            arp.append(op)

    posts = arp
    return posts


def post_item(request, item_id):
    try:
        p = Post.objects.only('id').get(id=item_id)
    except Exception, e:
        print str(e)
        return HttpResponse('{}')

    imo = p.get_image_500(api=True)

    data = {}

    if imo:
        data['id'] = p.id
        data['thumbnail'] = imo['url']
        data['hw'] = imo['hw']

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def post(request):
    data = {}
    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}
    data['objects'] = []

    before = request.GET.get('before', None)
    posts = []

    cur_user = None

    if not before:
        posts = Post.objects\
            .only(*Post.NEED_KEYS2)\
            .filter(id__in=[15877515])

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


def post2(request):
    data = {}
    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}
    data['objects'] = []

    if is_system_writable() is False:
        json_data = json.dumps(data, cls=MyEncoder)
        return HttpResponse(json_data, content_type="application/json")

    category_ids = []
    filters = {}
    cur_user = None
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
        cur_user = AuthCache.id_from_token(token=token)

    if category_id:
        category_ids = category_id.replace(',', ' ').split(' ')
        filters.update(dict(category_id__in=category_ids))

    if before:
        filters.update(dict(id__lt=before))

    if user_id:
        if cur_user:
            if Block.objects.filter(user_id=user_id, blocked_id=cur_user)\
                    .count():
                return HttpResponse('Blocked')

        sort_by = ['-id']
        filters.update(dict(user_id=user_id))
        if cur_user:
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

    posts = []

    if popular:
        posts = []
        for p in pop_posts:
            po = get_list_post2(p.pk, cur_user_id=cur_user)
            if po:
                posts.append(po)

        posts = get_list_post2(posts)

    elif not category_id and not popular and not user_id:
        if not before:
            before = 0
        pl = Post.latest(pid=before)
        posts = get_list_post2(pl, cur_user_id=cur_user)

    elif category_id and len(category_ids) == 1:
        if not before:
            before = 0
        pl = Post.latest(pid=before, cat_id=category_id)
        posts = get_list_post2(pl, cur_user_id=cur_user)

    else:
        posts = Post.objects\
            .only('id')\
            .filter(**filters).order_by(*sort_by)[:10]
        pl = [oib.id for oib in posts]

        posts = get_list_post2(pl, cur_user_id=cur_user)

    # if not user_id and not category_id:
    #     hot_post = None

    #     if cur_user:
    #         viewer_id = str(cur_user)
    #     else:
    #         viewer_id = str(get_user_ip(request, to_int=True))

    #     ad = Ad.get_ad(user_id=viewer_id)
    #     if ad:
    #         hot_post = int(ad.post_id)
    #         posts.append(get_list_post2([hot_post], cur_user_id=cur_user))

    thumb_size = int(request.GET.get('thumb_size', "236"))

    if thumb_size > 400:
        thumb_size = 500
    else:
        thumb_size = "236"

    data['objects'] = get_objects_list2(posts,
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

    posts = []

    if not before:
        posts = Post.objects\
            .only(*Post.NEED_KEYS2)\
            .filter(id__in=[15877515])

    thumb_size = request.GET.get('thumb_size', "100x100")

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       thumb_size=thumb_size, r=request)

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def likes(request):
    data = {}
    data['meta'] = {'limit': 20,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}
    data['objects'] = []

    if is_system_writable() is False:
        json_data = json.dumps(data, cls=MyEncoder)
        return HttpResponse(json_data, content_type="application/json")

    offset = int(request.GET.get('offset', 0))
    limit = 20

    next = {
        'url': "/pin/api/like/likes/?limit=%s&offset=%s" % (
            limit, offset + limit),
    }
    data['meta']['next'] = next['url']

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def notif(request):
    data = {}
    objects_list = []

    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def following(request, user_id=1):
    data = {}
    follow_cnt = 0

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

    data['objects'] = []

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def comments(request):
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    object_pk = int(request.GET.get('object_pk', 0))

    next = {
        'url': "/pin/api/com/comments/?limit=%s&offset=%s&object_pk=%s" % (
            limit, offset + limit, object_pk)
    }
    data = {}

    data['meta'] = {'limit': limit,
                    'next': next['url'],
                    'offset': offset,
                    'previous': '',
                    'total_count': 1000}

    data['objects'] = []

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def follower(request, user_id=1):
    data = {}
    follow_cnt = 0

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

    data['objects'] = []

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def search(request):
    data = {}

    query = request.GET.get('q', None)

    if not query:
        json_data = json.dumps(data, cls=MyEncoder)
        return HttpResponse(json_data, content_type="application/json")

    if query:
        data['objects'] = []

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def search2(request):
    query = request.GET.get('q', '')

    data = {}
    if query:
        data['objects'] = []

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def hashtag_top(request):
    tags = []
    data = {}
    o = []
    for t in tags:
        dt = {
            "tag": t[0],
            "count": t[1]
        }
        o.append(dt)
    data['objects'] = o

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def hashtag(request):
    query = request.GET.get('q', '')
    query = query.replace('#', '')
    data = {}

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


def search_posts(request):
    data = {}

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


@csrf_exempt
def password_reset(request, is_admin_site=False,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email_pin.html',
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
    return HttpResponse('error in change password')
    if is_system_writable() is False:
        return HttpResponse('error in change password')

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
    if is_system_writable() is False:
        return HttpResponse('1')

    user = None
    token = request.GET.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        raise Http404

    try:
        comment = Comments.objects.only('object_pk', 'user').get(pk=id)
    except Comments.DoesNotExist:
        return HttpResponse('Comment Does Not Exist', status=404)

    post = get_post_user_cache(post_id=comment.object_pk_id)
    comment_owner = int(comment.user_id)
    user_id = int(user.id)

    if post.user_id == user_id:
        # post owner like to remove a comment
        comment.delete()
        return HttpResponse(1, content_type="text/html")

    if comment_owner == user_id:
        # comment owner like to remove a comment
        comment.delete()
        return HttpResponse(1, content_type="text/html")

    return HttpResponse(0, content_type="text/html")


def block_user(request, user_id):
    return HttpResponse('1')
    if is_system_writable() is False:
        return HttpResponse('1')

    user = None
    token = request.GET.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        raise Http404

    Block.block_user(user_id=user.id, blocked_id=user_id)
    return HttpResponse('1')


def unblock_user(request, user_id):
    return HttpResponse('1')
    if is_system_writable() is False:
        return HttpResponse('1')

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
    data = {
        "objects": []
    }

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")


@cache_page(60 * 15)
def packages_old(request):
    data = {
        "objects": []
    }

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
    return HttpResponse("failed", content_type="text/html")
    if is_system_writable() is False:
        return HttpResponse("failed", content_type="text/html")

    user = None
    token = request.GET.get('token', '')
    price = int(request.GET.get('price', 0))
    baz_token = request.GET.get("baz_token", "")
    package_name = request.GET.get("package", "")
    if token:
        user = check_auth(request)

    # print user, token, baz_token, package_name

    if not user or not token or not baz_token or not package_name:
        return HttpResponse("default values erros", status=404)

    if package_name not in PACKS:
        return HttpResponse("package error", status=404)

    print PACKS[package_name]['price'], price

    if PACKS[package_name]['price'] != price:
        return HttpResponse("price error")

    # if PACKS[package_name]['price'] == price:
    if Bills2.objects.filter(trans_id=str(baz_token),
                             status=Bills2.COMPLETED).count() > 0:
        b = Bills2()
        b.trans_id = str(baz_token)
        b.user = user
        b.amount = PACKS[package_name]['price']
        b.status = Bills2.FAKERY
        b.save()
        return HttpResponse("bazzar token error", status=404)
    else:
        access_token = get_new_access_token()
        url = "https://pardakht.cafebazaar.ir/api/validate/ir.mohsennavabi.wisgoon/inapp\
               /%s/purchases/%s/?access_token=%s" % (package_name, baz_token, access_token)
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
                return HttpResponse("ex price error")

            if purchase_state == 0:
                b = Bills2()
                b.trans_id = str(baz_token)
                b.user = user
                b.amount = PACKS[package_name]['price']
                b.status = Bills2.COMPLETED
                b.save()

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
        except Exception:
            b = Bills2()
            b.trans_id = str(baz_token)
            b.user = user
            b.amount = PACKS[package_name]['price']
            b.status = Bills2.VALIDATE_ERROR
            b.save()
            return HttpResponse("ex price error")

        return HttpResponse("success full", content_type="text/html")

    return HttpResponse("failed", content_type="text/html")


@csrf_exempt
def save_as_ads(request, post_id):
    return HttpResponseForbidden("error in data")
    if is_system_writable() is False:
        return HttpResponseForbidden("error in data")

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
    token = request.GET.get('token', '')

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

    data['objects'] = objects

    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data, content_type="application/json")

    # return HttpResponse(json.dumps(data))


def get_phone_data(request):
    if is_system_writable() is False:
        return HttpResponse("not only :D", content_type="text/html")

    os = request.GET.get("os", "")
    app_version = request.GET.get("app_version", "")
    google_token = request.GET.get("google_token", "")
    token = request.GET.get("user_wisgoon_token", None)
    imei = request.GET.get("imei", "")
    android_version = request.GET.get("android_version", "")
    phone_serial = request.GET.get("phone_serial", "")
    phone_model = request.GET.get("phone_model", "").encode('ascii', 'ignore').decode('ascii')

    if not token:
        return HttpResponse("not only :D", content_type="text/html")

    user = AuthCache.user_from_token(token=token)

    if not user:
        return HttpResponse("user problem", content_type="text/html")

    if imei:
        if BannedImei.objects.filter(imei=imei).exists():
            u = User.objects.get(pk=user.id)
            if u.is_active:
                u.is_active = False
                u.save()

                # Log.ban_by_imei(actor=user, text=u.username,
                #                 ip_address=get_user_ip(request))

    try:
        upd = PhoneData.objects.only("hash_data").get(user=user)
        pfields = upd.get_need_fields()

        h_str = '%'.join([str(locals()[f]) for f in pfields])

        hash_str = hashlib.md5(h_str).hexdigest()

        if hash_str == upd.hash_data:
            return HttpResponse("allready updated", content_type="text/html")

    except PhoneData.DoesNotExist:
        print "not exists"

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
    if is_system_writable() is False:
        return HttpResponse("accepted", content_type="text/html")

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
    if is_system_writable() is False:
        return HttpResponse("logged out", content_type="text/html")

    token = request.GET.get("token", None)

    if token:
        user = AuthCache.user_from_token(token=token)
        PhoneData.objects.filter(user=user)\
            .update(logged_out=True)

    return HttpResponse("logged out", content_type="text/html")


def system(request):
    data = {
        "advertisement": {
            "adad": False,
            "agahist": True,
        }
    }

    return HttpResponse(json.dumps(data), content_type="application/json")
