from pin.tools import AuthCache
from pin.models import Post, Category
from django.conf import settings
from django.core.urlresolvers import reverse
from pin.api_tools import abs_url, media_abs_url

from pin.cacheLayer import UserDataCache
from pin.models_redis import LikesRedis
from pin.api6.tools import get_next_url, category_get_json

from daddy_avatar.templatetags.daddy_avatar import get_avatar
from pin.api6.http import return_json_data, return_bad_request

from haystack.query import SearchQuerySet


def get_list_post(pl, from_model='latest'):
    arp = []

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS2).get(id=pll))
        except Exception:
            pass

    posts = arp
    return posts


def get_objects_list(posts, cur_user_id, r=None):

    objects_list = []
    for p in posts:
        if not p:
            continue

        try:
            if p.is_pending():
                continue
        except Post.DoesNotExist:
            continue

        o, u = {}, {}

        o['id'] = p.id
        o['text'] = p.text
        o['cnt_comment'] = 0 if p.cnt_comment == -1 else p.cnt_comment
        o['timestamp'] = p.timestamp

        u['id'] = p.user_id
        u['avatar'] = media_abs_url(get_avatar(p.user_id, size=100))
        u['username'] = UserDataCache.get_user_name(p.user_id)

        o['user'] = u
        try:
            o['url'] = p.url
        except Exception, e:
            print str(e)
            if r:
                print r.get_full_path()
            o['url'] = None
        o['like'] = p.cnt_like
        o['like_with_user'] = False
        o['status'] = p.status

        try:
            o['is_ad'] = False  # p.is_ad
        except Exception, e:
            # print str(e)
            o['is_ad'] = False

        o['permalink'] = abs_url(reverse("api-5-post-item",
                                         kwargs={"item_id": p.id}))

        if cur_user_id:
            o['like_with_user'] = LikesRedis(post_id=p.id)\
                .user_liked(user_id=cur_user_id)

        o['images'] = {}
        try:
            p_500 = p.get_image_500(api=True)
            o['images']['low_resolution'] = p_500
            o['images']['low_resolution']['url'] = media_abs_url(p_500['url'])
            o['images']['low_resolution']['height'] = int(p_500['hw'].split("x")[0])
            o['images']['low_resolution']['width'] = int(p_500['hw'].split("x")[1])
            del(o['images']['low_resolution']['hw'])
            del(o['images']['low_resolution']['h'])

            p_236 = p.get_image_236(api=True)
            o['images']['thumbnail'] = p_236
            o['images']['thumbnail']['url'] = media_abs_url(p_236['url'])
            o['images']['thumbnail']['height'] = int(p_236['hw'].split("x")[0])
            o['images']['thumbnail']['width'] = int(p_236['hw'].split("x")[1])
            del(o['images']['thumbnail']['hw'])
            del(o['images']['thumbnail']['h'])

            p_original = p.get_image_sizes()
            o['images']['original'] = p_original
            o['images']['original']['url'] = media_abs_url(p.image)
        except Exception, e:
            continue

        o['category'] = category_get_json(cat_id=p.category_id)
        objects_list.append(o)

    return objects_list


def latest(request):
    cur_user = None
    last_item = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': 1000}

    before = request.GET.get('before', None)
    token = request.GET.get('token', '')

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if not before:
        before = 0

    pl = Post.latest(pid=before)
    posts = get_list_post(pl, from_model=settings.STREAM_LATEST)

    data['objects'] = get_objects_list(posts,
                                       cur_user_id=cur_user,
                                       r=request)

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-5-post-latest',
                                            token=token, before=last_item)

    return return_json_data(data)


def friends(request):
    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    before = request.GET.get('before', None)
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)
    else:
        return return_bad_request()

    if not cur_user:
        return return_bad_request()

    if before:
        idis = Post.user_stream_latest(user_id=cur_user, pid=before)
    else:
        idis = Post.user_stream_latest(user_id=cur_user)

    posts = get_list_post(idis, from_model=settings.STREAM_LATEST)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-5-post-friends',
                                            token=token, before=last_item)

    return return_json_data(data)


def category(request, category_id):
    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    before = request.GET.get('before', None)
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if not before:
        before = 0

    pl = Post.latest(pid=before, cat_id=category_id)
    from_model = "%s_%s" % (settings.STREAM_LATEST_CAT, category_id)
    posts = get_list_post(pl, from_model=from_model)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-5-post-category',
                                            token=token, before=last_item,
                                            url_args={
                                                "category_id": category_id
                                            })

    return return_json_data(data)


def choices(request):
    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    before = request.GET.get('before', None)
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if not before:
        before = 0

    pl = Post.home_latest(pid=before)
    posts = get_list_post(pl)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-5-post-choices',
                                            token=token, before=last_item)

    return return_json_data(data)


def search(request):
    row_per_page = 20
    query = request.GET.get('q', '')
    offset = int(request.GET.get('offset', 0))
    next_offset = offset + 1 * row_per_page

    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    before = request.GET.get('before', None)
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if not before:
        before = 0

    posts = SearchQuerySet().models(Post)\
        .filter(content__contains=query)[offset:next_offset]

    idis = []
    for pmlt in posts:
        idis.append(pmlt.pk)

    posts = Post.objects.filter(id__in=idis).only(*Post.NEED_KEYS_WEB)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)

    if data['objects']:
        data['meta']['next'] = get_next_url(url_name='api-5-post-search',
                                            token=token, offset=next_offset)

    return return_json_data(data)


def item(request, item_id):
    cur_user = None
    data = {}
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    posts = get_list_post([item_id])

    try:
        data = get_objects_list(posts, cur_user_id=cur_user,
                                r=request)[0]
    except IndexError:
        return_json_data({})

    return return_json_data(data)
