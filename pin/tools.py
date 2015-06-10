import os
import time

from datetime import datetime
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import User
# from django.db.models import F

from tastypie.models import ApiKey

from user_profile.models import Profile
from pin.models import Category, Block, Log, Post
from pin.model_mongo import UserMeta, FixedAds

from daddy_avatar.templatetags import daddy_avatar
from statsd import StatsClient

statsd = StatsClient(host="79.127.125.104")

user_keys = {}
USERDATA_TIMEOUT = 300

CARBON_SERVER = '127.0.0.1'
CARBON_PORT = 2003

# if settings.DEBUG:
#     from feedreader.task_cel_local import inc_prof
# else:
#     from feedreader.task_cel import inc_prof

# def inc_user_cnt_like(user_id):
#     inc_prof.delay(user_id)
#     #print "inc for ", user_id
#     # Profile.objects.filter(user_id=user_id)\
#     #     .update(cnt_like=F('cnt_like')+1, score=F('score')+10)

# def dec_user_cnt_like(user_id):
#     Profile.objects.filter(user_id=user_id)\
#         .update(cnt_like=F('cnt_like')-1, score=F('score')-10)


def get_post_user_cache(post_id):
    cache_str = "post_user_%d" % int(post_id)
    cache_data = cache.get(cache_str)
    if cache_data:
        # print "get from cached data"
        return cache_data
    try:
        post = Post.objects.only('user').get(pk=post_id)
        cache.set(cache_str, post, 86400)
        return post
    except Post.DoesNotExist:
        cache.delete(cache_str)
        raise Post.DoesNotExist


def post_after_delete(post, user, ip_address=None):
    Log.post_delete(post=post, actor=user, ip_address=ip_address)
    if post.user_id == user.id:
        return
    from tasks import send_notif_bar

    send_notif_bar(user=post.user.id, type=4, post=post.id,
                   actor=11253, post_image=post.get_image_236())


def log_act(path,):
    statsd.incr(path)


def get_fixed_ads():
    c_name = "fixed_post"
    c_e = cache.get(c_name)
    if c_e:
        c_name_p = "fixed_post_%d" % int(c_e)
        c_p = cache.incr(c_name_p)
        if (c_p % 100) == 0:
            FixedAds.objects(post=c_e).update(set__cnt_view=c_p)

        return c_e
    return None


def create_filename(filename):
    d = datetime.now()
    folder = "%d/%d/%d/%d" % (d.year, d.month, d.day, d.hour)
    paths = []
    paths.append("%s/pin/temp/o/" % (settings.MEDIA_ROOT))
    paths.append("%s/pin/temp/t/" % (settings.MEDIA_ROOT))
    paths.append("%s/pin/images/o/" % (settings.MEDIA_ROOT))
    paths.append("%s/pin/images/t/" % (settings.MEDIA_ROOT))
    for path in paths:
        abs_path = "%s%s" % (path, folder)
        if not os.path.exists(abs_path):
            try:
                os.makedirs(abs_path, mode=0777)
            except Exception, e:
                print str(e)
    filestr = "%s/%f" % (folder, time.time())
    filestr = filestr.replace('.', '')
    filename = "%s%s" % (filestr, os.path.splitext(filename)[1])
    return filename


def userdata_cache(user, field=None, size=100):
    cache_key = 'userd_%s_%s' % (user, size)

    if cache_key in user_keys:
        data = user_keys[cache_key]
    else:
        data = cache.get(cache_key)

    if data:
        if field is not None:
            return data[field]

        return data
    else:
        avatar = daddy_avatar.get_avatar(user, size=size)
        username = get_username(user)

        value = [avatar, username]
        user_keys[cache_key] = value
        cache.set(cache_key, value, USERDATA_TIMEOUT)

        if field is not None:
            return value[field]

        return value

    return []


def get_username(user):
    if isinstance(user, (int, long)):
        try:
            user = User.objects.only('username').get(pk=user)
        except User.DoesNotExist:
            return user

    try:
        profile = Profile.objects.only('name').get(user_id=user.id)
        if not profile:
            username = user.username
        else:
            username = profile.name
    except Profile.DoesNotExist:
        username = user.username

    if not username:
        username = user.username

    return username


def get_request_timestamp(request):
    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    return timestamp


def get_request_pid(request):
    try:
        pid = int(request.GET.get('pid', 0))
    except ValueError:
        pid = 0
    return pid


def get_user_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', None)
    return ip
    # return request.META.get('REMOTE_ADDR', None)


class MyCache(object):
    LONG_TIME = 60 * 60 * 24


class CatCache(MyCache):

    @classmethod
    def get_cat(cls, cat_id):
        cc_str = "cat_%d" % cat_id
        cc_cache = cache.get(cc_str)
        if cc_cache:
            return cc_cache

        cat = Category.objects.get(id=cat_id)
        cache.set(cc_str, cat, cls.LONG_TIME)
        return cat


class AuthCache(MyCache):
    TTL_TOKEN = 60 * 60
    TTL_AVATAR = 60 * 60 * 24
    TTL_USERNAME = 60 * 60 * 24

    @classmethod
    def get_username(cls, user_id):
        cun_str = "%s%d" % (settings.USER_NAME_CACHE, user_id)
        c_str = cache.get(cun_str)
        if c_str:
            return c_str

        if isinstance(user_id, (int, long)):
            try:
                user = User.objects.only('username').get(pk=user_id)
            except User.DoesNotExist:
                print "not exists tools line 154: ", user_id
                return "noname"

        try:
            profile = Profile.objects.only('name').get(user_id=user.id)
            if not profile:
                username = user.username
            else:
                username = profile.name
        except Profile.DoesNotExist:
            username = user.username

        if not username:
            username = user.username

        cache.set(cun_str, username, cls.TTL_USERNAME)
        return username

    @classmethod
    def avatar(cls, user_id, size=100):
        ca_str = "ava_%d_%d" % (user_id, size)
        c_avatar = cache.get(ca_str)
        if c_avatar:
            return c_avatar

        avatar = daddy_avatar.get_avatar(user_id, size=size)
        cache.set(ca_str, avatar, cls.TTL_AVATAR)
        return avatar

    @classmethod
    def id_from_token(cls, token):
        if not token:
            return None

        ct_str = "tuid_%s" % str(token)
        c_token = cache.get(ct_str)
        if c_token:
            return c_token
        else:
            try:
                api = ApiKey.objects.get(key=token)
            except ApiKey.DoesNotExist:
                return None
            cache.set(ct_str, api.user_id, cls.TTL_TOKEN)
            return api.user_id

    @classmethod
    def user_from_token(cls, token):
        if not token:
            return None

        # ct_str = "tu_%s" % str(token)
        # c_token = cache.get(ct_str)
        # if c_token:
            # return c_token
        # else:
        try:
            api = ApiKey.objects.get(key=token)
            u = api.user
            return u
        except ApiKey.DoesNotExist:
            return None

        return None


def check_block(user_id, blocked_id):
    block_cnt = Block.objects.filter(user_id=user_id,
                                     blocked_id=blocked_id).count()
    # print "block cnt is:", block_cnt
    if block_cnt:
        return True

    return False


def get_user_meta(user_id):
    try:
        user_meta = UserMeta.objects.get(user=user_id)
    except UserMeta.DoesNotExist:
        user_meta = UserMeta.objects.create(user=user_id)
    except UserMeta.MultipleObjectsReturned:
        user_meta = UserMeta.objects.filter(user=user_id).first()

    return user_meta


def is_mobile(request):
    agent = request.META.get('HTTP_USER_AGENT')
    if 'android' in agent.lower():
        return True
    else:
        return False
