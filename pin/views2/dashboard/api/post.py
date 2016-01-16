from django.views.decorators.csrf import csrf_exempt

from pin.api6.http import return_json_data, return_not_found, return_un_auth,\
    return_bad_request
from pin.api6.tools import post_item_json, get_next_url, get_simple_user_object,\
    get_profile_data
from pin.views2.dashboard.api.tools import post_reporter_user, get_reported_posts,\
    check_admin, ads_group_by, calculate_post_percent, cnt_post_deleted_by_user,\
    cnt_post_deleted_by_admin, get_ads, delete_posts, undo_report


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
        post_item['user'] = get_simple_user_object(post.user.id)
        post_item['user']['profile'] = get_profile_data(post.user.profile, post.user.id)
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

    if date and ended:

        data['objects'] = get_ads(before, date, ended)

        if len(data['objects']) == 20:
            before = int(before) + 20
            token = request.GET.get('token', '')
            data['meta']['next'] = get_next_url(url_name='dashboard-api-post-ads-show',
                                                before=before,
                                                token=token)
        return return_json_data(data)
    else:
        return return_bad_request()


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


@csrf_exempt
def delete_post(request):
    if not check_admin(request):
        return return_un_auth()

    status = delete_posts(request)
    return return_json_data({"status": status})


@csrf_exempt
def post_undo(request):
    if not check_admin(request):
        return return_un_auth()

    status = undo_report(request)
    return return_json_data({'status': status})
