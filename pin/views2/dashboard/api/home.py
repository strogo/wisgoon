import datetime
import redis
from django.conf import settings

from pin.api6.http import return_json_data, return_un_auth
from pin.views2.dashboard.api.tools import today_new_users, today_bills,\
    today_new_posts, today_likes, today_blocks, today_follow,\
    today_view_pages,\
    today_comments, check_admin

from pin.models import Post

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


def dashboard_home(request):

    if not check_admin(request):
        return return_un_auth()

    data = {}
    objects = {}
    today = str(datetime.date.today())

    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    objects['home_queue'] = {'cnt_post': r_server.llen(Post.HOME_QUEUE_NAME),
                             'more_info': 'url'}

    objects['today_users'] = {'cnt_users': today_new_users(today),
                              'more_info': 'url'}
    objects['today_posts'] = {'cnt_posts': today_new_posts(today),
                              'more_info': 'url'}
    objects['today_likes'] = {'cnt_likes': today_likes(today),
                              'more_info': 'url'}
    objects['today_follow'] = {'cnt_follows': today_follow(today),
                               'more_info': 'url'}
    objects['today_blocks'] = {'cnt_blocks': today_blocks(today),
                               'more_info': 'url'}
    objects['today_view_pages'] = {'cnt_view_pages': today_view_pages(today),
                                   'more_info': 'url'}
    objects['today_bills'] = {'cnt_bills': today_bills(today),
                              'more_info': 'url'}
    objects['today_comments'] = {'cnt_comments': today_comments(today),
                                 'more_info': 'url'}
    data['objects'] = objects

    return return_json_data(data)
