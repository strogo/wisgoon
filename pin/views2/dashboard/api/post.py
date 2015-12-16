
from pin.api6.http import return_json_data, return_not_found, return_un_auth
from pin.api6.tools import post_item_json, get_next_url
from pin.views2.dashboard.api.tools import post_reporter_user, get_reported_posts,\
    check_admin, ads_group_by, calculate_post_percent


def reported(request):
    if not check_admin(request):
        return return_un_auth()

    post_reporter_list = []
    data = {'next': '', 'posts': ''}

    reported_posts = get_reported_posts(request)
    if not reported_posts:
        return return_not_found()
    for post in reported_posts:
        post_item = post_item_json(post)
        post_item['reporter'], post_item['reporter_scores'] = post_reporter_user(post.id)
        post_item['cnt_report'] = post.report
        post_reporter_list.append(post_item)

    data['posts'] = post_reporter_list

    if len(post_reporter_list) == 20:
        before = int(request.GET.get('before', 0)) + 20
        token = request.GET.get('token', '')
        data['next'] = get_next_url(url_name='dashboard-api-post-reported',
                                    before=before, token=token)
    return return_json_data(data)


def enable_ads(request):
    if not check_admin(request):
        return return_un_auth()
    point_list = []
    ads = ads_group_by('start', False)
    data = {}
    for ad in ads:
        timestamp = int(ad['start'].strftime('%s')) * 1000
        point_list.append([timestamp, ad['cnt_ad']])
    data['data'] = point_list
    data['name'] = 'Advertising'
    return return_json_data(data)


def disable_ads(request):
    if not check_admin(request):
        return return_un_auth()
    point_list = []
    ads = ads_group_by('start', True)
    data = {}
    for ad in ads:
        timestamp = int(ad['start'].strftime('%s')) * 1000
        point_list.append([timestamp, ad['cnt_ad']])
    data['data'] = point_list
    data['name'] = 'Advertising'
    return return_json_data(data)


def post_of_category(request):
    posts = calculate_post_percent()
    return return_json_data(posts)
