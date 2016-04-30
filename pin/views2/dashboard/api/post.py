from __future__ import division

# from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from pin.models import Post, Report, Category, SubCategory, ReportedPost, ReportedPostReporters,\
    PhoneData, BannedImei, UserHistory
from pin.api6.http import (return_bad_request, return_json_data,
                           return_not_found, return_un_auth)
from pin.api6.tools import (get_next_url, get_simple_user_object,
                            post_item_json)
from pin.views2.dashboard.api.tools import get_profile_data, get_post_reporers
from pin.views2.dashboard.api.tools import (ads_group_by,
                                            check_admin, cnt_post_deleted_by_admin,
                                            cnt_post_deleted_by_user,
                                            delete_posts, get_ads,
                                            undo_report
                                            )
from user_profile.models import Profile

from haystack.query import SearchQuerySet


@csrf_exempt
def post_item(request, post_id):
    data = {}

    posts = Post.objects.get(id=post_id)
    user_profile = Profile.objects.get(user=posts.user)

    post = post_item_json(posts.id)

    post['user']['cnt_admin_deleted'] = cnt_post_deleted_by_admin(posts.user_id)
    post['user']['cnt_post'] = user_profile.cnt_post
    data = post

    return return_json_data(data)


def new_reporte(request):
    before = int(request.GET.get('before', 0))

    posts = ReportedPost.objects.only('id')[before: (before + 1) * 20]

    data = {
        'meta': {'limit': 20,
                 'next': '',
                 'total_count': ReportedPost.objects.filter().count()},
        'objects': []
    }

    obj = []
    imei_user = []

    # user_name = []
    user = None

    for report in posts:
        post = post_item_json(report.post.id)

        user_profile = Profile.objects.get(user=report.post.user)

        try:
            phone_data = PhoneData.objects.filter(user=report.post.user)
        except Exception as e:
            print str(e)

        for user in phone_data:
            # user_name.append(user.user.username)
            imei_user.append(user.user.username)
            post['user']['imei'] = user.imei
        post['reporters'] = get_post_reporers(report)

        post['user']['cnt_admin_deleted'] = cnt_post_deleted_by_admin(report.post.user_id)
        if user:
            post['user']['list_imei'] = imei_user
            banned_imi = BannedImei.objects.filter(imei=user.imei).exists()
            post['user']['banned_imi'] = banned_imi
        else:
            post['user']['list_imei'] = None
            post['user']['banned_imi'] = None

        post['user']['cnt_post'] = user_profile.cnt_post
        post['user']['banned_profile'] = user_profile.banned
        post['user']['is_active'] = report.post.user.is_active

        obj.append(post)
        # print obj
    data['objects'] = obj
    if len(data) == 20:
        token = request.GET.get('token', '')
        data['meta']['next'] = get_next_url(url_name='ddashboard-api-post-new_reporte',
                                            before=before + 20, token=token)
    return return_json_data(data)


def reported(request):
    from daddy_avatar.templatetags.daddy_avatar import get_avatar
    from pin.api_tools import media_abs_url
    if not check_admin(request):
        return return_un_auth()
    # type_report1 = sys report
    # type_report2 = user report

    before = int(request.GET.get('before', 0))
    # type_report = int(request.GET.get('type', 0))
    reported_posts = None

    post_reporter_list = []
    data = {}
    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': Post.objects.filter(report__gte=1).count()}

    reported_posts = Post.objects.filter(report__gte=1).only('id', 'report')\
        .order_by('-report')[before: (before + 1) * 20]

    # if type_report == 2:
    #     reported_posts = Post.objects.filter(report__lt=30)\
    #         .only('id', 'report')\
    #         .order_by('-report')[before: (before + 1) * 20]

    if not reported_posts:
        return return_not_found()

    for post in reported_posts:
        reporter_ids = Report.objects.values_list('id', flat=True)\
            .filter(post_id=post.id)[:5]

        reporter_avatar = []
        for reporter_id in reporter_ids:
            reporter_avatar.append(media_abs_url(get_avatar(reporter_id, size=64),
                                                 check_photos=True))

        # total_scores = Profile.objects.filter(user_id__in=reporter_ids)\
        #     .aggregate(scores=Sum('score'))

        total_scores = 50

        post_item = post_item_json(post.id)
        post_item['cnt_report'] = post.report
        post_item['total_scores'] = total_scores
        # post_item['reporter_avatar'] = reporter_avatar
        post_reporter_list.append(post_item)

    data['objects'] = post_reporter_list

    if len(post_reporter_list) == 20:
        token = request.GET.get('token', '')
        data['meta']['next'] = get_next_url(url_name='dashboard-api-post-reported',
                                            before=before + 20, token=token)
    return return_json_data(data)


def post_reporter_user(request, post_id):
    from pin.api_tools import abs_url
    from django.core.urlresolvers import reverse

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
        users['reporter']['permalink'] = abs_url(reverse("pin-absuser",
                                                 kwargs={"user_name": users['reporter']['username']}
                                                         ))
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
    before = int(request.GET.get('before', 0))
    token = request.GET.get('token', False)
    data['meta'] = {'limit': '20', 'next': '', 'total_count': ''}

    if date:
        extra_data = {}
        if token:
            extra_data['token'] = token

        extra_data['url_name'] = 'dashboard-api-post-ads-show'
        extra_data['date'] = date

        data['objects'] = get_ads(before, date)

        extra_data['before'] = before - 20 if before > 0 else "0"
        data['meta']['previous'] = get_next_url(**extra_data)

        extra_data['before'] = before + 20 if before > 0 else 20
        data['meta']['next'] = get_next_url(**extra_data)

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
    if not start_date or not end_date:
        return return_bad_request()

    categories = dict(Category.objects.filter(parent__title=cat_name)
                      .values_list('id', 'title'))

    query = SearchQuerySet().models(Post)\
        .filter(category_i__in=categories.keys())\
        .narrow("timestamp_i:[{} TO {}]".format(str(start_date)[:10], str(end_date)[:10]))\
        .facet('category_i')

    post_of_cat = query.facet_counts()
    count_of_posts = query.count()

    if post_of_cat or count_of_posts != 0:
        for key, value in post_of_cat['fields']['category_i']:
            if int(key) in categories:
                percent = (value * 100) / count_of_posts
                cat_list.append({"name": categories[int(key)], "y": percent})

    data['objects'] = cat_list

    return return_json_data(data)


def post_of_sub_category(request):
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}
    data['objects'] = {}
    start_date = request.GET.get("start_date", False)
    end_date = request.GET.get("end_date", False)
    if not start_date or not end_date:
        return return_bad_request()

    cat_lvl1 = SubCategory.objects.all()
    categories = {}
    result = []

    for cat in cat_lvl1:
        child = Category.objects\
            .filter(parent=cat).values('title', 'id')
        categories[cat.title] = list(child)

    query = SearchQuerySet().models(Post)\
        .narrow("timestamp_i:[{} TO {}]".format(str(start_date)[:10], str(end_date)[:10]))\
        .facet('category_i')

    post_of_cat = query.facet_counts()
    count_of_posts = query.count()

    if post_of_cat or count_of_posts != 0:
        cat_cnt_post = dict(post_of_cat['fields']['category_i'])

        for cat in categories:
            sum_of_post = 0

            for value in categories[cat]:
                value['cnt_post'] = cat_cnt_post.get(str(value['id']), 0)
                sum_of_post += int(value['cnt_post'])

            percentage = (sum_of_post * 100) / count_of_posts
            result.append({"name": cat, "y": percentage})

    data['objects'] = result
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


@csrf_exempt
def post_undo_new(request):
    if not check_admin(request):
        return return_un_auth()

    post_ids = request.POST.getlist('post_ids')

    if not post_ids:
        return return_bad_request(message=_('enter post id'))

    if post_ids:
        reported_posts = ReportedPost.objects.filter(post_id__in=post_ids)

        for post in reported_posts:

            posts_report = ReportedPostReporters.objects\
                .filter(reported_post=post).values_list('user_id', flat=True)

            user_history = UserHistory.objects.filter(user_id__in=posts_report)

            for user in user_history:
                user.neg_report += 1
                user.save()

            post.delete()
    return return_json_data({'status': True,
                             'message': _('successfully undo report')})


@csrf_exempt
def delete_post_new(request):
    if not check_admin(request):
        return return_un_auth()

    post_ids = request.POST.getlist('post_ids')

    if not post_ids:
        return return_bad_request(message=_('enter post id'))

    if post_ids:
        reported_posts = ReportedPost.objects.filter(post_id__in=post_ids)
        post = Post.objects.get(id__in=post_ids)
        print post

        for posts in reported_posts:

            posts_report = ReportedPostReporters.objects\
                .filter(reported_post=posts).values_list('user_id', flat=True)

            user_history = UserHistory.objects.filter(user_id__in=posts_report)
        for user in user_history:
            user.pos_report += 1
            user.admin_post_deleted += 1
            user.save()
        posts.delete()
        post.delete()
        return return_json_data({'status': True,
                                 'message': _('successfully delete report')})
