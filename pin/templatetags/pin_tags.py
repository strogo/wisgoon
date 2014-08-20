import datetime
from calverter import Calverter
from urlparse import urlparse

from django import template
from django.contrib.auth.models import User
from django.core.cache import cache
from django.template import Library
from django.template.defaultfilters import stringfilter
from django.utils.text import normalize_newlines
from django.utils.safestring import mark_safe

from pin.models import Likes as pin_likes
from pin.model_mongo import Notif
from user_profile.models import Profile

from pin.tools import userdata_cache
from pin.tools import AuthCache


register = Library()


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
            #liked = pin_likes.objects.filter(user=user, item=item).count()
            liked = pin_likes.user_in_likers(post_id=item, user_id=user.id)
            if liked:
                return 'btn-danger'
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
            liked = pin_likes.user_in_likers(post_id=item, user_id=user.id)
            #liked = pin_likes.objects.filter(user=user, post=item).count()
            if liked:
                return 'btn-danger'
            else:
                return ''
        except template.VariableDoesNotExist:
            return ''

register.tag('user_post_like', user_post_like)


@register.filter
def get_user_notify(userid):
    notify = Notif.objects.all().filter(owner=userid, seen=False).count()
    return notify


@register.filter
def get_username(user):

    if isinstance(user, (unicode)):
        user = int(user)

    if isinstance(user, (int, long)):
        #user = User.objects.only('email').get(pk=user)
        user_str = "user_name_%d" % (user)
        user_cache = cache.get(user_str)
        if user_cache:
            user = user_cache
        else:
            user = User.objects.only('username').get(pk=user)
            cache.set(user_str, user, 60*60*24)

    profile_str = "profile_name_%d" % (user.id)
    profile_cache = cache.get(profile_str)
    if profile_cache:
        return profile_cache

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
    #gd = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    gd = value
    cal = Calverter()
    jd = cal.gregorian_to_jd(gd.year, gd.month, gd.day)

    d = cal.jd_to_jalali(jd)
    d = "%s/%s/%s" % (d[0], d[1], d[2])
    return d


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
