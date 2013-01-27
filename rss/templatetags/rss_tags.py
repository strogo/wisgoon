# -*- coding:utf-8 -*-
from django.template import Library,Node
from urlparse import urlparse
import datetime
from rss.models import Subscribe, Feed, Likes
from pin.models import Likes as pin_likes, Notify
from django.contrib.auth.models import User
from django.template.base import TemplateSyntaxError
from django import template
from django.utils.text import normalize_newlines
from django.utils.safestring import mark_safe
from django.template.defaultfilters import stringfilter
from calverter import Calverter
from user_profile.models import Profile

register = Library()

def user_feed_subs(parser, token):
    try:
        tag_name, feed = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    
    return UserFeedSubs(feed)

class UserFeedSubs(template.Node):
    def __init__(self, feed):
        self.feed = template.Variable(feed)
    
    def render(self, context):
        try:
            feed = int(self.feed.resolve(context))
            user = context['user']
            subs = Subscribe.objects.filter(user=user,feed=feed).count()
            if subs:
                context['user_feed_subs_status'] = 1
                #return 1
            else:
                context['user_feed_subs_status'] = 0
                #return 0
        except template.VariableDoesNotExist:
            return ''
        
        return ''
    
register.tag('user_feed_subs', user_feed_subs)

def user_item_like(parser, token):
    try:
        # split_contents() knows not to split quoted strings.
        tag_name, item = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    
    return UserItemLike(item)

class UserItemLike(template.Node):
    def __init__(self, item):
        self.item = template.Variable(item)

    def render(self, context):
        try:
            item = int(self.item.resolve(context))
            user=context['user']
            liked = Likes.objects.filter(user=user, item=item).count()
            if liked :
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
        raise template.TemplateSyntaxError("%r tag requires exactly two arguments" % token.contents.split()[0])
    
    return UserPostLike(item)

class UserPostLike(template.Node):
    def __init__(self, item):
        self.item = template.Variable(item)

    def render(self, context):
        try:
            item = int(self.item.resolve(context))
            user=context['user']
            liked = pin_likes.objects.filter(user=user, post=item).count()
            if liked :
                return 'btn-danger'
            else:
                return ''
        except template.VariableDoesNotExist:
            return ''

register.tag('user_post_like', user_post_like)

@register.filter
def get_user_notify(userid):
    notify = Notify.objects.all().filter(user_id=userid, seen=False).count()
    return notify

@register.filter
def human_farsi(text):
    text = text.replace('seconds', u'ثانیه')
    text = text.replace('days', u'روز')
    text = text.replace('day', u'روز')
    text = text.replace('ago', u'قبل')
    text = text.replace('a minute', u'یک دقیقه')
    text = text.replace('months', u'ماه')
    text = text.replace('weeks', u'هفته')
    text = text.replace('week', u'هفته')
    text = text.replace('minutes', u'دقیقه')
    text = text.replace('an hour', u'یک ساعت')
    text = text.replace('hours', u'ساعت')
    #print text
    #text = text.replace('month', 'ماه')
    return text

@register.filter
def get_username(user):
    try:
        profile=Profile.objects.get(user_id=user.id)
        username=profile.name
    except Profile.DoesNotExist:
        username=user.username
    return username

@register.filter
def get_host(value):
    o = urlparse(value)
    if hasattr(o, 'netloc'):
        return o.netloc
    else:
        return ''

@register.filter
def date_from_timestamp(value):
    return datetime.datetime.fromtimestamp(int(value)).strftime('%Y-%m-%d %H:%M:%S')

@register.filter
def jalali_mysql_date(value):
    #gd = datetime.datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
    gd = value
    cal = Calverter()
    jd = cal.gregorian_to_jd(gd.year, gd.month, gd.day)
    
    d = cal.jd_to_jalali(jd)
    d = "%s/%s/%s" % (d[0], d[1], d[2])
    return d

def user_feeds(parser, token):
    return UserFeeds(parser, token)

class UserFeeds(Node):
    def __init__(self, parser, token):
        pass
        
    def render(self, context):
        user=context['user']
        try:
            context['user_feeds'] = Subscribe.objects.filter(user=user).all()[:10]
        except:
            context['user_feeds'] = ""
        return ''

register.tag('get_user_feeds', user_feeds)


def all_feeds(parser, token):
    return AllFeeds(parser, token)

class AllFeeds(Node):
    def __init__(self, parser, token):
        pass
        
    def render(self, context):            
        context['all_feeds'] = Feed.objects.all().order_by('-id')[:10]
        return ''

register.tag('get_all_feeds', all_feeds)


def recomend_feeds(parser, token):
    return RecomendFeeds()

class RecomendFeeds(Node):
    def render(self, context):
        context['recomend_feeds'] = Feed.objects.all().order_by('-followers')[:10]
        return ''

register.tag('get_recomend_feeds', recomend_feeds)


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
