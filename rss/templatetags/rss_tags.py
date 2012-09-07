from django.template import Library,Node
from urlparse import urlparse
import datetime
from rss.models import Subscribe, Feed
from django.contrib.auth.models import User

register = Library()

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
    
    
def user_feeds(parser, token):
    return UserFeeds(parser, token)

class UserFeeds(Node):
    def __init__(self, parser, token):
        pass
        
    def render(self, context):
        user=context['user']
	try:
            context['user_feeds'] = Subscribe.objects.filter(user=user).all()
	except:
	    context['user_feeds'] = ""
        return ''

register.tag('get_user_feeds', user_feeds)



def recomend_feeds(parser, token):
    return RecomendFeeds()

class RecomendFeeds(Node):
    def render(self, context):
        context['recomend_feeds'] = Feed.objects.all().order_by('-followers')
        return ''

register.tag('get_recomend_feeds', recomend_feeds)
