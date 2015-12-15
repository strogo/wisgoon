import datetime

from pin.api6.http import return_json_data, return_un_auth
from pin.views2.dashboard.api.tools import today_new_users, today_bills,\
    today_new_posts, today_likes, today_blocks, today_follow, today_view_pages,\
    today_comments, check_admin


def dashboard_home(request):

    if not check_admin(request):
        return return_un_auth()

    data = {}
    today = str(datetime.date.today())

    data['today_users'] = {'cnt_users': today_new_users(today),
                           'more_info': 'url'}
    data['today_posts'] = {'cnt_posts': today_new_posts(today),
                           'more_info': 'url'}
    data['today_likes'] = {'cnt_likes': today_likes(today),
                           'more_info': 'url'}
    data['today_follow'] = {'cnt_likes': today_follow(today),
                            'more_info': 'url'}
    data['today_blocks'] = {'cnt_likes': today_blocks(today),
                            'more_info': 'url'}
    data['today_view_pages'] = {'cnt_view_pages': today_view_pages(today),
                                'more_info': 'url'}
    data['today_bills'] = {'cnt_today_bills': today_bills(today),
                           'more_info': 'url'}
    data['today_comments'] = {'cnt_today_bills': today_comments(today),
                              'more_info': 'url'}

    return return_json_data(data)
