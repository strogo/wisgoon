
from pin.api6.http import return_json_data, return_not_found, return_un_auth
from pin.api6.tools import post_item_json, get_next_url
from pin.views2.dashboard.api.tools import post_reporter_user, get_reported_posts,\
    check_admin, ads_group_by, calculate_post_percent, cnt_post_deleted_by_user,\
    cnt_post_deleted_by_admin, get_ads


def reported(request):
    if not check_admin(request):
        return return_un_auth()

    post_reporter_list = []
    data = {}
    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': ''}

    reported_posts = get_reported_posts(request)
    if not reported_posts:
        return return_not_found()

    for post in reported_posts:
        post_item = post_item_json(post)
        post_item['reporter'], post_item['reporter_scores'] = post_reporter_user(post.id)
        post_item['cnt_report'] = post.report
        post_item['user']['score'] = post.user.profile.score
        post_item['user']['status'] = post.user.profile.banned
        post_item['user']['cnt_deleted'] = cnt_post_deleted_by_user(post.user.id)
        post_item['user']['cnt_admin_deleted'] = cnt_post_deleted_by_admin(post.user.id)
        post_reporter_list.append(post_item)

    data['objects'] = post_reporter_list

    if len(post_reporter_list) == 20:
        before = int(request.GET.get('before', 0)) + 20
        token = request.GET.get('token', '')
        data['meta']['next'] = get_next_url(url_name='dashboard-api-post-reported',
                                            before=before, token=token)
    return return_json_data(data)


def enable_ads(request):

    if not check_admin(request):
        return return_un_auth()

    point_list = []
    data = {}
    objects = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}
    ads = ads_group_by('start', False)
    for ad in ads:
        timestamp = int(ad['start'].strftime('%s')) * 1000
        point_list.append([timestamp, ad['cnt_ad']])
    objects['data'] = point_list
    objects['name'] = 'Advertising'
    data['objects'] = objects
    return return_json_data(data)


def disable_ads(request):
    if not check_admin(request):
        return return_un_auth()
    point_list = []
    data = {}
    objects = {}
    data['meta'] = {'limit': '20:',
                    'next': '',
                    'total_count': ''}
    ads = ads_group_by('start', True)

    for ad in ads:
        timestamp = int(ad['start'].strftime('%s')) * 1000
        point_list.append([timestamp, ad['cnt_ad']])

    objects['data'] = point_list
    objects['name'] = 'Advertising'
    data['objects'] = objects

    return return_json_data(data)


def show_ads(request):
    if not check_admin(request):
        return return_un_auth()

    data = {}
    date = request.GET.get('date', False)
    ended = request.GET.get('ended', False)
    before = request.GET.get('before', 0)
    data['meta'] = {'limit': '', 'next': '', 'total_count': ''}

    if not date and not ended:
        return return_not_found()

    data['objects'] = get_ads(before, date, ended)

    if len(data['objects']) == 20:
        before = int(before) + 20
        token = request.GET.get('token', '')
        data['meta']['next'] = get_next_url(url_name='dashboard-api-post-ads-show',
                                            before=before, token=token)
    return return_json_data(data)


def post_of_category(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}
    data['objects'] = {}
    data['objects']['drill_down'], data['objects']['sub_cat'], data['meta']['total_count'] = calculate_post_percent()
    return return_json_data(data)
