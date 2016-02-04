from django.views.decorators.csrf import csrf_exempt

from pin.api6.http import (return_bad_request, return_json_data,
                           return_not_found, return_un_auth)
from pin.api6.tools import (get_next_url, get_profile_data,
                            get_simple_user_object,
                            post_item_json)
from pin.models import Post, Report
from pin.views2.dashboard.api.tools import (ads_group_by, calculate_post_percent,
                                            check_admin, cnt_post_deleted_by_admin,
                                            cnt_post_deleted_by_user,
                                            delete_posts, get_ads,
                                            post_reporter_user, undo_report
                                            )
from user_profile.models import Profile


def reported(request):
    if not check_admin(request):
        return return_un_auth()

    before = int(request.GET.get('before', 0))
    post_reporter_list = []
    data = {}
    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': ''}

    reported_posts = Post.objects.filter(report__gte=1)\
        .order_by('-id')[before: (before + 1) * 20]
    if not reported_posts:
        return return_not_found()

    for post in reported_posts:
        post_item = post_item_json(post)
        post_item['cnt_report'] = post.report
        # post_item['user']['cnt_deleted'] = cnt_post_deleted_by_user(post.user.id)
        # post_item['user']['cnt_admin_deleted'] = cnt_post_deleted_by_admin(post.user.id)
        post_reporter_list.append(post_item)

    data['objects'] = post_reporter_list

    if len(post_reporter_list) == 20:
        token = request.GET.get('token', '')
        data['meta']['next'] = get_next_url(url_name='dashboard-api-post-reported',
                                            before=before + 20, token=token)
    return return_json_data(data)


def post_reporter_user(request, post_id):
    if not check_admin(request):
        return return_un_auth()
    reporters = Report.objects.filter(post_id=post_id)
    user_list = []
    users = {}
    score = 0
    for reporter in reporters:
        users['reporter'] = get_simple_user_object(reporter.user.id)
        users['reporter']['score'] = reporter.user.profile.score
        score += reporter.user.profile.score
        user_list.append(users)
    users['reporter_scores'] = score
    return return_json_data(users)


def post_user_details(request, user_id):
    if not check_admin(request):
        return return_un_auth()
    user = {}
    try:
        profile = Profile.objects.get(user_id=user_id)
    except:
        return return_not_found()
    user['profie'] = get_profile_data(profile, user_id)
    user['cnt_deleted'] = cnt_post_deleted_by_user(user_id)
    user['cnt_admin_deleted'] = cnt_post_deleted_by_admin(user_id)
    return return_json_data(user)


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
