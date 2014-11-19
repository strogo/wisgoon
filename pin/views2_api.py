#-*- coding: utf-8 -*-
import json
import re
import datetime
import time
import redis
from hashlib import md5

from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.template.response import TemplateResponse
from django.http import HttpResponse, HttpResponseForbidden, Http404
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from sorl.thumbnail import get_thumbnail

from pin.tools import userdata_cache, AuthCache, CatCache
from pin.models import Post, Category, Likes, Stream, Follow, Comments
from pin.model_mongo import Notif

from daddy_avatar.templatetags.daddy_avatar import get_avatar

r_server = redis.Redis(settings.REDIS_DB, db=11)


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
    #thumb_size = thumb_size
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
            print "get_thumb", o_image, thumb_size, settings.API_THUMB_QUALITY
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
            print str(e), im

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


def get_objects_list(posts, cur_user_id, thumb_size, r=None):
    # cache_key = md5(json.dumps(posts)).hexdigest()
    # list_cache_str = "olist_%s" % (cache_key)
    # cache_list = cache.get(list_cache_str)
    # if cache_list:
    #     return cache_list
    
    objects_list = []
    for p in posts:
        o = {}
        o['id'] = p['id']
        o['text'] = p['text']
        o['cnt_comment'] = 0 if p['cnt_comment'] == -1 else p['cnt_comment']
        o['image'] = p['image']

        o['user_avatar'] = get_avatar(p['user_id'], size=100)
        o['user_name'] = AuthCache.get_username(user_id=p['user_id'])

        o['timestamp'] = p['timestamp']

        o['user'] = p['user_id']
        try:
            o['url'] = p['url']
        except Exception, e:
            print str(e)
            if r:
                print r.get_full_path()
            o['url'] = None
        o['like'] = p['cnt_like']
        o['likers'] = None
        o['like_with_user'] = False
        o['status'] = p['status']

        o['permalink'] = "/pin/%d/" % p['id']
        o['resource_uri'] = "/pin/api/post/%d/" % p['id']

        if cur_user_id:
            o['like_with_user'] = Likes.user_in_likers(post_id=p['id'], user_id=cur_user_id)

        if not thumb_size:
            thumb_size = "236"

        o_image = p['image']

        imo = get_thumb(o_image, thumb_size, settings.API_THUMB_QUALITY)

        if imo:
            o['thumbnail'] = imo['thumbnail'].replace('/media/', '')
            o['hw'] = imo['hw']
        else:
            print "*******"
            print "we dont have imo", p['id'], o_image, imo
            print "*******"
            continue

        o['category'] = Category.get_json(cat_id=p['category_id'])
        objects_list.append(o)

    # cache.set(list_cache_str, objects_list, 600)

    return objects_list


def get_list_post(pl, from_model='latest'):
    arp = []
    pl_str = '2_'.join(pl)
    cache_pl = md5(pl_str).hexdigest()
    #print cache_stream_str, cache_stream_name

    posts = cache.get(cache_pl)
    if posts:
        return posts

    for pll in pl:
        try:
            arp.append(Post.objects.values(*Post.NEED_KEYS).get(id=pll))
        except Exception, e:
            print str(e), 'line 182', pll
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
    cache_ttl = 120
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
        cur_user = AuthCache.id_from_token(token=token)

    if category_id:

        category_ids = category_id.replace(',', ' ').split(' ')
        filters.update(dict(category_id__in=category_ids))

    if before:
        filters.update(dict(id__lt=before))

    if user_id:
        sort_by = ['-timestamp']
        filters.update(dict(user_id=user_id))
        if cur_user:
            if int(cur_user) == int(user_id):
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
            date_from = dt_now - datetime.timedelta(hours=8)

        if date_from:
            start_from = time.mktime(date_from.timetuple())
            filters.update(dict(timestamp__gt=start_from))

    cache_stream_str = "v2%s_%s" % (str(filters), sort_by)

    cache_stream_name = md5(cache_stream_str).hexdigest()
    #print cache_stream_str, cache_stream_name

    posts = cache.get(cache_stream_name)
    #print cache_stream_str, cache_stream_name, posts

    if not category_id and not popular and not user_id:
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
                .values(*Post.NEED_KEYS)\
                .filter(**filters).order_by(*sort_by)[:10]

            cache.set(cache_stream_name, posts, 86400)
    else:
        posts = Post.objects\
            .values(*Post.NEED_KEYS)\
            .filter(**filters).order_by(*sort_by)[:10]
        # if not user_id and not category_id:
        #     # hot_post = Post.get_hot(values=True)
        #     hot_post = Post.objects\
        #         .values(*Post.NEED_KEYS)\
        #         .filter(id=2416517)
        #     if hot_post:
        #         posts = list(hot_post) + list(posts)

    if not user_id:
        hot_post = Post.objects\
            .values(*Post.NEED_KEYS)\
            .filter(id=3178722)
        if hot_post:
            posts = list(hot_post) + list(posts)

    thumb_size = int(request.GET.get('thumb_size', "236"))
    #print "thumb_size", thumb_size
    if thumb_size > 400:
        thumb_size = 500
    else:
        thumb_size = "236"

    #cache.set(cache_stream_name, posts, cache_ttl)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user, thumb_size=thumb_size, r=request)
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
        .values(*Post.NEED_KEYS)\
        .filter(id=post_id)

    thumb_size = int(request.GET.get('thumb_size', "236"))
    if thumb_size > 400:
        thumb_size = 500
    else:
        thumb_size = "236"

    #cache.set(cache_stream_name, posts, cache_ttl)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user, thumb_size=thumb_size)
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def friends_post(request):
    r = request
    #print "we are in post"

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    next = {
        'url': "/api/post/friends_post/?limit=%s&offset=%s" % (limit, offset + limit),
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

    if before:
        s = Stream.objects.get(user=cur_user, post_id=before)
        stream = Stream.objects.filter(user=cur_user, date__lt=s.date)\
            .order_by('-date')[offset:offset + limit]
        sort_by = ['-timestamp']
    else:
        stream = Stream.objects.filter(user=cur_user)\
            .order_by('-date')[offset:offset + limit]

    idis = []
    for p in stream:
        idis.append(int(p.post_id))

    posts = Post.objects\
        .values(*Post.NEED_KEYS)\
        .filter(id__in=idis).order_by('-id')[:limit]

    thumb_size = request.GET.get('thumb_size', "100x100")

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user, thumb_size=thumb_size, r=request)

    #data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)


def likes(request):

    before = request.GET.get('before', None)
    post_id = request.GET.get('post_id', None)
    offset = int(request.GET.get('offset', 0))
    #limit = int(request.GET.get('limit', 20))
    limit = 20

    next = {
        'url': "/pin/api/like/likes/?limit=%s&offset=%s" % (limit, offset+limit),
    }

    data = {}
    data['meta'] = {'limit': 20,
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

    Notif.objects.filter(owner=cur_user,seen=False).update(set__seen=True)


    rf = ['id', 'text', 'cnt_comment', 'image',
          'user_id', 'cnt_like', 'category_id']

    for p in notifs:
        try:
            cur_p = Post.objects.values(*Post.NEED_KEYS).get(id=p.post)
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
        o['timestamp'] = cur_p['timestamp']
        o['url'] = ""
        o['likers'] = None
        o['like_with_user'] = False

        #o['resource_uri'] = "/pin/api/notif/notify/%d/" % cur_p['id']
        o['resource_uri'] = "/pin/api/post/%d/" % cur_p['id']
        o['permalink'] = "/pin/%d/" % cur_p['id']

        if cur_user:
            o['like_with_user'] = Likes.user_in_likers(post_id=cur_p['id'], user_id=cur_user)

        #thumb_size = request.GET.get('thumb_size', "100x100")
        thumb_size = "236"
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


def comments(request):
    data = {}

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    object_pk = int(request.GET.get('object_pk', 0))

    next = {
        'url': "/pin/api2/com/comments/?limit=%s&offset=%s&object_pk=%s" % (limit, offset+limit, object_pk)
    }

    data['meta'] = {'limit': limit,
                    'next': next['url'],
                    'offset': offset,
                    'previous': '',
                    'total_count': 1000}

    objects_list = []

    for com in Comments.objects.filter(object_pk_id=object_pk)[offset:offset+limit]:
        o = {}
        o['id'] = com.id
        o['object_pk'] = com.object_pk_id
        o['score'] = com.score

        com_date = str(com.submit_date)
        com_date = com_date.replace(' ', 'T')
        com_date = com_date.split('+')[0]
        #print com_date

        
        o['submit_date'] = com_date
        o['comment'] = com.comment
        o['user_url'] = com.user_id
        o['user_avatar'] = get_avatar(com.user_id, size=100)
        o['user_name'] = AuthCache.get_username(com.user_id)
        o['resource_uri'] = "/pin/api/com/comments/1/"

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
    cur_user = None
    limit = request.GET.get('limit', 20)
    start = request.GET.get('start', 0)

    data = {}
    import pysolr
    solr = pysolr.Solr('http://localhost:8983/solr/wisgoon_user', timeout=10)
    query = request.GET.get('q', '')
    if query:
        q_str = "*%s*" % query
        fq = 'username_s:*%s* name_s:*%s*' % (query, query)
        results = solr.search("*:*", fq=fq, rows=limit, start=start, sort="score_i desc")

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
                # o['follow_by_user'] = Follow.objects\
                #     .filter(follower_id=cur_user, following_id=r['id']).exists()
            else:
                o['follow_by_user'] = False

            data['objects'].append(o)

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
