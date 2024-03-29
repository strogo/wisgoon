import json
from hashlib import md5
from urlparse import urlparse

from django.core.cache import cache
from django.conf import settings
from django.core.urlresolvers import reverse

from sorl.thumbnail import get_thumbnail

from daddy_avatar.templatetags.daddy_avatar import get_avatar
from pin.tools import AuthCache
from pin.models import Category, Post, Likes


def get_cat_json(cat_id):
    jccs = "json_cat3_%s" % cat_id
    jcc = cache.get(jccs)
    if jcc:
        return jcc

    cat = Category.objects.get(id=cat_id)
    cat_json = {
        'id': cat.id,
        'image': media_abs_url(cat.image.url),
        'resource_uri': abs_url("/pin/apic/category/" + str(cat.id) + "/"),
        'title': cat.title,
    }
    cache.set(jccs, cat_json, 86400)
    return cat_json


def get_next_url(url_name, before, token):
    n_url = reverse(url_name)
    n_url_p = n_url + "?before=%s" % (before)
    if token:
        n_url_p = n_url_p + "&token=%s" % (token)
    return abs_url(n_url_p)


def abs_url(url, api=True):
    if not url.startswith('http://'):
        if api:
            return settings.SITE_URL + url
        else:
            return settings.SITE_URL + url


def get_domain_from_url(url):
    parsed_uri = urlparse(url)
    domain = parsed_uri.netloc
    return domain


def media_abs_url(url, check_photos=False, static=False):
    if static:
        cur_base_url = settings.STATIC_DOMAIN
    else:
        cur_base_url = settings.SITE_URL

    if not static:
        if url.startswith('http://'):
            new_url = url
        elif not url.startswith('/media/'):
            new_url = cur_base_url + '/media/' + url
        elif url.startswith('/media/'):
            new_url = cur_base_url + url
    else:
        new_url = cur_base_url + url

    base_domain = get_domain_from_url(new_url)

    if check_photos:
        if "photos01" in new_url:
            new_url = new_url.replace(base_domain, "photos01.wisgoon.com")
        elif "photos02" in new_url:
            new_url = new_url.replace(base_domain, "photos02.wisgoon.com")
        elif "photos03" in new_url:
            new_url = new_url.replace(base_domain, "photos03.wisgoon.com")
        elif "saturn" in new_url:
            new_url = new_url.replace(base_domain, "saturn.wisgoon.com")
        elif "jupiter" in new_url:
            new_url = new_url.replace(base_domain, "jupiter.wisgoon.com")
        elif "mars" in new_url:
            new_url = new_url.replace(base_domain, "mars.wisgoon.com")

    return new_url


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        return json.JSONEncoder.default(self, obj)


def get_user_dict(user_id):
    o = {}
    o['avatar'] = media_abs_url(get_avatar(user_id, size=100))
    o['name'] = AuthCache.get_username(user_id=user_id)
    o['id'] = user_id

    return o


def get_r_data(request):
    before = request.GET.get('before', None)
    cur_user = None
    thumb_size = int(request.GET.get('thumb_size', "236"))

    if thumb_size > 400:
        thumb_size = 500
    else:
        thumb_size = "236"

    if before is None:
        before = 0

    token = request.GET.get('token', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    return before, cur_user, thumb_size, before, token


def get_cache(key):
    if settings.ENABLE_CACHING:
        return cache.get(key)

    return None


def get_list_post(pl, from_model='latest'):
    arp = []
    pl_str = '32_'.join(pl)
    cache_pl = md5(pl_str).hexdigest()

    posts = get_cache(cache_pl)
    if posts:
        return posts

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS2).get(id=pll))
        except Exception:
            pass

    posts = arp
    cache.set(cache_pl, posts, 3600)
    return posts


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
                default_image = 'noPhoto_max.jpg'
                dfsize = "500x500"
            else:
                default_image = 'noPhoto_mini.jpg'
                dfsize = "236x236"

            imo = {
                'thumbnail': default_image,
                'hw': dfsize
            }
    return imo


def get_objects_list(posts, cur_user_id, thumb_size, r=None):

    objects_list = []
    for p in posts:
        o = {}
        o['id'] = p.id
        o['text'] = p.text
        o['cnt_comment'] = 0 if p.cnt_comment == -1 else p.cnt_comment
        o['user'] = get_user_dict(p.user_id)
        o['timestamp'] = p.timestamp
        o['url'] = p.url
        o['like'] = p.cnt_like
        o['like_with_user'] = False
        o['status'] = p.status
        o['permalink'] = abs_url("/pin/%d/" % p.id)
        o['resource_uri'] = abs_url(reverse('api-3-item', args=[p.id]))

        if cur_user_id:
            o['like_with_user'] = Likes.user_in_likers(post_id=p.id,
                                                       user_id=cur_user_id)

        o_image = p.image
        if not p.get_image_236():
            continue
        if not p.get_image_500():
            continue

        o['images'] = {
            "original": {
                "url": media_abs_url(p.image)
            },
            "small": {
                "url": p.get_image_236()['url'],
                "hw": p.get_image_236()['hw'],
            },
            "medium": {
                "url": p.get_image_500()['url'],
                "hw": p.get_image_500()['hw']
            }
        }

        o['category'] = get_cat_json(cat_id=p.category_id)
        objects_list.append(o)

    return objects_list
