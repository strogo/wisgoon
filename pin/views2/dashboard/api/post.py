from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Sum

from pin.api6.http import (return_bad_request, return_json_data,
                           return_not_found, return_un_auth)
from pin.api6.tools import (get_next_url, get_simple_user_object,
                            post_item_json)
from pin.models import Post, Report, Category
from pin.views2.dashboard.api.tools import get_profile_data
from pin.views2.dashboard.api.tools import (ads_group_by,
                                            check_admin, cnt_post_deleted_by_admin,
                                            cnt_post_deleted_by_user,
                                            delete_posts, get_ads,
                                            undo_report
                                            )
from user_profile.models import Profile

from haystack.query import SearchQuerySet


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
        reporter_ids = Report.objects.values_list('id', flat=True)\
            .filter(post_id=post.id)

        total_scores = Profile.objects.filter(user_id__in=reporter_ids)\
            .aggregate(scores=Sum('score'))

        post_item = post_item_json(post)
        post_item['cnt_report'] = post.report
        post_item['total_scores'] = total_scores['scores']
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
    user_list = []
    users = {}
    data = {}
    limit = 5
    token = request.GET.get('token', '')
    before = int(request.GET.get("before", 0))
    data['meta'] = {'limit': limit,
                    'next': '',
                    'total_count': ''}

    reporters = Report.objects.filter(post_id=post_id)\
        .order_by('-id')[before: before + limit]

    for reporter in reporters:
        users['reporter'] = get_simple_user_object(reporter.user.id)
        users['reporter']['score'] = reporter.user.profile.score
        user_list.append(users)

    data['objects'] = users

    data['meta']['next'] = get_next_url(url_name='dashboard-api-post-reporters',
                                        before=before + limit, token=token,
                                        url_args={'post_id': post_id})

    return return_json_data(data)


def post_user_details(request, user_id):
    if not check_admin(request):
        return return_un_auth()
    user = {}
    try:
        profile = Profile.objects.get(user_id=user_id)
    except:
        return return_not_found()
    user['profile'] = get_profile_data(profile, enable_imei=True)
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
    before = request.GET.get('before', 0)
    data['meta'] = {'limit': '', 'next': '', 'total_count': ''}

    if date:

        data['objects'] = get_ads(before, date)

        if len(data['objects']) == 20:
            before = int(before) + 20
            token = request.GET.get('token', '')
            data['meta']['next'] = get_next_url(url_name='dashboard-api-post-ads-show',
                                                before=before,
                                                token=token)
        return return_json_data(data)
    else:
        return return_bad_request()


def post_of_category(request, cat_name):

    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}
    data['objects'] = {}
    cat_list = []
    start_date = request.GET.get("start_date", False)
    end_date = request.GET.get("end_date", False)
    if not start_date or end_date:
        return return_bad_request()

    categories = dict(Category.objects.filter(parent__title=cat_name)
                      .values_list('id', 'title'))

    post_of_cat = SearchQuerySet().models(Post)\
        .filter(category_i__in=categories.keys(),
                timestamp_i__lte=str(start_date),
                timestamp_i__gte=str(end_date))\
        .facet('category_i').facet_counts()

    count_of_posts = SearchQuerySet().models(Post).facet('category_i').count()
    for key, value in post_of_cat['fields']['category_i']:
        if int(key) in categories:
            percent = (value * 100) / count_of_posts
            cat_list.append({categories[int(key)]: percent})

    data['objects'] = {"name": cat_name, "data": cat_list}

    return return_json_data(data)


def post_of_sub_category(request):
    post = {}
    post_list = []
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}
    data['objects'] = {}
    start_date = request.GET.get("start_date", False)
    end_date = request.GET.get("end_date", False)
    if not start_date or end_date:
        return return_bad_request()

    post_of_sub_cat = Post.objects\
        .values('category__parent__title')\
        .filter(timestamp__lte=str(start_date),
                timestamp__gte=str(end_date))\
        .annotate(cnt_post=Count('category__parent')).order_by('-id')

    count_of_posts = SearchQuerySet().models(Post).facet('category_i').count()

    for post in post_of_sub_cat:
        post['y'] = (post['cnt_post'] * 100) / count_of_posts
        post['name'] = post['category__parent__title']
        # post['drilldown'] = post['category__parent__title']
        try:
            del post['cnt_post']
            del post['category__parent__title']
        except KeyError:
            pass
        post_list.append(post)

    data['objects'] = post_list
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
