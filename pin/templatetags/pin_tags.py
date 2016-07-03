# -*- coding: utf-8 -*-
import emoji
import datetime
import re

from calverter import Calverter
from urlparse import urlparse
import khayyam
from django import template
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.text import normalize_newlines
from django.utils.safestring import mark_safe

from pin.models import Likes as pinLikes
# from pin.model_mongo import NotifCount
from user_profile.models import Profile

from pin.tools import userdata_cache
from pin.tools import AuthCache
from pin.models_redis import NotificationRedis

User = get_user_model()
register = Library()


@register.filter
def keyvalue(dict, key):
    return dict[key]


@register.filter
def urlize_hashtag(obj):
    return mark_safe(urlize_text(obj))
urlize_hashtag.is_safe = True
urlize_hashtag = stringfilter(urlize_hashtag)


def urlize_text(text):
    hashtag_pattern = re.compile(ur'(?i)#(\w+)', re.UNICODE)
    text = hashtag_pattern.sub(hashtag_urlize, text)
    return text


def emojize_text(text):
    text = emoji.emojize(text)
    return text


def hashtag_urlize(m):
    hashtag = m.group(0)
    hashtag = hashtag.replace('#', '')

    url = reverse('hashtags', args=[hashtag])

    return '<a class="tag-item" href="%s">&#35;%s</a>' % (url, hashtag)


def user_item_like(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, item = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly two arguments"
            % token.contents.split()[0])

    return UserItemLike(item)


class UserItemLike(template.Node):
    def __init__(self, item):
        self.item = template.Variable(item)

    def render(self, context):
        try:
            item = int(self.item.resolve(context))
            user = context['user']
            liked = pinLikes.user_in_likers(post_id=item, user_id=user.id)
            if liked:
                return 'user-liked'
            else:
                return ''
        except template.VariableDoesNotExist:
            return ''

register.tag('user_item_like', user_item_like)


def user_post_like(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, item = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError(
            "%r tag requires exactly two arguments"
            % token.contents.split()[0])

    return UserPostLike(item)


class UserPostLike(template.Node):
    def __init__(self, item):
        self.item = template.Variable(item)

    def render(self, context):
        try:
            item = int(self.item.resolve(context))
            user = context['user']
            liked = pinLikes.user_in_likers(post_id=item, user_id=user.id)
            if liked:
                return 'user-liked'
            else:
                return ''
        except template.VariableDoesNotExist:
            return ''

register.tag('user_post_like', user_post_like)


@register.filter
def get_user_notify(userid):
    return NotificationRedis(user_id=userid).get_notif_count()
    # try:
    #     notify = NotifCount.objects.filter(owner=userid).first().unread
    # except Exception:
    #     notify = 0
    # return notify


@register.filter
def get_image(post_id):
    from pin.api6.cache_layer import PostCacheLayer
    from pin.models import Post
    from pin.api_tools import media_abs_url
    p_236 = None
    if post_id:
        cp = PostCacheLayer(post_id=post_id)
        cache_post = cp.get()
        if cache_post:
            p_236 = cache_post['images']['thumbnail']['url']

        try:
            post = Post.objects.get(id=post_id)
            p_236 = post.get_image_236()
            p_236 = media_abs_url(p_236['url'], check_photos=True)
        except Post.DoesNotExist:
            p_236 = None
    return p_236


@register.filter
def get_user_name(user_id):
    user_id = int(user_id)
    from pin.cacheLayer import UserDataCache
    return UserDataCache.get_user_name(user_id=user_id)


@register.filter
def get_username(user):

    if isinstance(user, (unicode, str)):
        user = int(user)

    if isinstance(user, (int, long)):
        user_str = "user_name_%d" % (user)
        user_cache = cache.get(user_str)
        if user_cache:
            user = user_cache
        else:
            user = User.objects.only('username').get(pk=user)
            cache.set(user_str, user, 60 * 60 * 24)

    profile_str = "profile_name_%d" % (user.id)
    profile_cache = cache.get(profile_str)
    if profile_cache:
        # print "we have cache for profile"
        return profile_cache

    # print "we dont have cache for profile"
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

    cache.set(profile_str, username, 60 * 60)

    return username


@register.filter
def get_absusername(user):

    if isinstance(user, (unicode, str)):
        user = int(user)

    if isinstance(user, (int, long)):
        user_str = "user_name_%d" % (user)
        user_cache = cache.get(user_str)
        if user_cache:
            user = user_cache
        else:
            try:
                user = User.objects.only('username').get(pk=user)
            except User.DoesNotExist:
                return 'wisgoon'
            cache.set(user_str, user, 60 * 60 * 24)

    username = user.username
    return username


@register.filter
def get_cache_avatar(user, size=30):
    return AuthCache.avatar(user, size=size)


@register.filter
def get_userdata_avatar(user, size=30):
    return userdata_cache(user, 0, size=size)


@register.filter
def get_userdata_name(user, size=30):
    return userdata_cache(user, 1)


@register.filter
def get_host(value):
    o = urlparse(value)
    if hasattr(o, 'netloc'):
        return o.netloc
    else:
        return ''


@register.filter
def date_from_timestamp(value):
    return datetime.datetime.fromtimestamp(int(value))\
        .strftime('%Y-%m-%d %H:%M:%S')


@register.filter
def jalali_mysql_date(value):
    gd = value
    cal = Calverter()
    jd = cal.gregorian_to_jd(gd.year, gd.month, gd.day)

    d = cal.jd_to_jalali(jd)
    d = "%s/%s/%s" % (d[0], d[1], d[2])
    return d


@register.filter
def check_official(user_id):
    pass


@register.filter
def date_filter(index, time=False):
    import pytz
    tz = pytz.timezone('Asia/Tehran')

    if not isinstance(index, datetime.datetime):
        index = datetime.datetime.fromtimestamp(index)
        t1 = index
    else:
        t1 = index.astimezone(tz).replace(tzinfo=None)

    t2 = datetime.datetime.today()
    try:
        t1 = index.astimezone(tz).replace(tzinfo=None)
    except:
        t1 = tz.localize(index).replace(tzinfo=None)
        pass
    t2 = datetime.datetime.today().replace(tzinfo=None)

    days = (t2 - t1).days
    if not days:
        diff = (t2 - t1)
        hour, minutue = divmod(diff.days * 86400 + diff.seconds, 3600)
        if hour:
            return '%d ساعت پیش' % hour
        minutue, second = divmod(diff.days * 86400 + diff.seconds, 60)
        if minutue:
            return '%d دقیقه پیش' % minutue
        elif not minutue and second:
            return '%d ثانیه پیش' % second
        else:
            return 'لحظاتی پیش'
    else:
        if days > 31:
            if time:
                try:
                    return khayyam.JalaliDatetime.from_datetime(t1).strftime("%d %B %Y- %H:%M")
                except AttributeError:
                    return t1
            else:
                try:
                    return khayyam.JalaliDatetime.from_datetime(t1).strftime("%B %Y")
                except AttributeError:
                    return t1
        else:
            weeks = days / 7
            if days > 7:
                return '%d هفته پیش' % weeks
            else:
                return '%d روز پیش' % days


@register.filter
def get_follow_status(user_id, following_id):
    from pin.models import Follow
    fstatus = Follow.objects.filter(follower_id=user_id, following_id=following_id).exists()
    return fstatus


@register.filter
def get_user_posts(user_id):
    from pin.models import Post
    user_posts = Post.objects.only(*Post.NEED_KEYS_WEB).filter(user=user_id).order_by('-id')[:4]
    html = '<div class="flw_posts">'
    for x in xrange(4):
        try:
            p = user_posts[x].get_image_236()
            if p['h'] > 236:
                cl = 'p'
            else:
                cl = 'l'
            html += '<a class="%s" href="%s"><img src="%s" alt="%s" /></a>' % (cl, user_posts[x].get_absolute_url(), p['url'], user_posts[x].text)
        except:
            html += '<a class="empty"></a>'

    html += '</div>'
    return html


@register.filter
def pn(value):
    value = str(value)
    value = value.replace('1', '۱')
    value = value.replace('2', '۲')
    value = value.replace('3', '۳')
    value = value.replace('4', '۴')
    value = value.replace('5', '۵')
    value = value.replace('6', '۶')
    value = value.replace('7', '۷')
    value = value.replace('8', '۸')
    value = value.replace('9', '۹')
    value = value.replace('0', '۰')
    return value


@register.filter
def check_block(blocker_id, blocked_id):
    from pin.tools import check_block

    return check_block(blocker_id, blocked_id)


@register.filter
def get_ban(txt):
    try:
        t = txt.split("||")
        result = t[1]
    except:
        result = txt

    return result


def remove_newlines(text):
    """
    Removes all newline characters from a block of text.
    """
    # First normalize the newlines using Django's nifty utility
    normalized_text = normalize_newlines(text)
    # Then simply remove the newlines like so.
    return mark_safe(normalized_text.replace('\n', ' '))
remove_newlines.is_safe = True
remove_newlines = stringfilter(remove_newlines)
register.filter(remove_newlines)


@register.filter
def user_posts_for_email(user_id):
    from pin.models import Post
    posts = Post.objects.filter(user_id=user_id).order_by('-id')
    h1 = 0
    h2 = 0
    tb1_html = '<table>'
    tb2_html = '<table>'
    html = ''
    for p in posts:
        b = p.get_image_236()
        if h1 < h2:
            tb1_html += '<tr><td valign="top"><a href="%s"><img style="border-radius:10px;margin-bottom:5px;box-shadow:2px 2px 3px #000;" src="%s" alt="%s" /></a></td></tr>' % (p.get_absolute_url(), b['url'], p.text)
            h1 += b['h']
        else:
            tb2_html += '<tr><td valign="top"><a href="%s"><img style="border-radius:10px;margin-bottom:5px;box-shadow:2px 2px 3px #000;" src="%s" alt="%s" /></a></td></tr>' % (p.get_absolute_url(), b['url'], p.text)
            h2 += b['h']

    tb1_html += '</table>'
    tb2_html += '</table>'
    html += '<table align="center"><tr><td valign="top">%s</td><td valign="top">%s</td></tr></table>' % (tb1_html, tb2_html)
    return html


@register.filter
def timestamp_to_datetime(timestamp):
    import pytz

    tz = pytz.timezone('Asia/Tehran')
    converted = tz.localize(datetime.datetime.fromtimestamp(int(timestamp)))

    t1 = converted.astimezone(tz).replace(tzinfo=None)
    t2 = datetime.datetime.today()

    days = (t2 - t1).days

    if not days:
        diff = (t2 - t1)
        hour, minutue = divmod(diff.days * 86400 + diff.seconds, 3600)

        if hour:
            return '%d ساعت پیش' % hour

        minutue, second = divmod(diff.days * 86400 + diff.seconds, 60)
        if minutue:
            return '%d دقیقه پیش' % minutue

        elif not minutue and second:
            return '%d ثانیه پیش' % second

        else:
            return 'لحظاتی پیش'
    else:
        if days > 31:

            try:
                return khayyam.JalaliDatetime.fromtimestamp(timestamp).strftime("%B %Y")
            except AttributeError:
                return t1

        else:
            weeks = days / 7
            if days > 7:
                return '%d هفته پیش' % weeks
            else:
                return '%d روز پیش' % days
