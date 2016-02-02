import datetime

from django.db.models import Count

from pin.model_mongo import MonthlyStats
from pin.models import Report, Post, Ad, Log
from pin.api6.tools import get_simple_user_object, get_profile_data,\
    post_item_json
from pin.tools import post_after_delete, get_user_ip
from django.contrib.auth.models import User
from django.db.models import Q


def check_admin(request):
    from django.conf import settings
    status = False
    current_user = None

    if settings.DEBUG:
        from pin.tools import AuthCache
        token = request.GET.get('token', '')
        if token:
            current_user = AuthCache.user_from_token(token=token)
        else:
            current_user = request.user
    else:
        current_user = request.user

    if current_user and current_user.is_superuser:
        status = True
    return status


def today_new_users(today):
    try:
        cnt_today_users = MonthlyStats.objects\
            .get(date=(today), object_type=MonthlyStats.USER)
        cnt_today_users = cnt_today_users.count
    except:
        cnt_today_users = 0

    return cnt_today_users


def today_new_posts(today):
    try:
        cnt_today_posts = MonthlyStats.objects\
            .get(date=today, object_type=MonthlyStats.POST)
        cnt_today_posts = cnt_today_posts.count
    except:
        cnt_today_posts = 0

    return cnt_today_posts


def today_likes(today):
    try:
        cnt_today_likes = MonthlyStats.objects\
            .get(date=today, object_type=MonthlyStats.LIKE)
        cnt_today_likes = cnt_today_likes.count
    except:
        cnt_today_likes = 0

    return cnt_today_likes


def today_blocks(today):
    try:
        cnt_today_blocks = MonthlyStats.objects\
            .get(date=today, object_type=MonthlyStats.BLOCK)
        cnt_today_blocks = cnt_today_blocks.count
    except:
        cnt_today_blocks = 0

    return cnt_today_blocks


def today_follow(today):
    try:
        cnt_today_follow = MonthlyStats.objects\
            .get(date=today, object_type=MonthlyStats.FOLLOW)
        cnt_today_follow = cnt_today_follow.count
    except:
        cnt_today_follow = 0

    return cnt_today_follow


def today_view_pages(today):
    try:
        today_view = MonthlyStats.objects\
            .get(date=today, object_type=MonthlyStats.VIEW)
        today_view = today_view.count
    except:
        today_view = 0

    return today_view


def today_bills(today):
    try:
        today_cnt_bills = MonthlyStats.objects\
            .get(date=today, object_type=MonthlyStats.BILL)
        today_cnt_bills = today_cnt_bills.count
    except:
        today_cnt_bills = 0

    return today_cnt_bills


def today_comments(today):
    try:
        today_cnt_comments = MonthlyStats.objects\
            .get(date=today, object_type=MonthlyStats.COMMENT)
        today_cnt_comments = today_cnt_comments.count
    except:
        today_cnt_comments = 0
    return today_cnt_comments


def preparing_chart_points(points):

    point_list = []
    for point in points:
        date = str(point.date)[:10]
        date = datetime.datetime.strptime(date, "%Y-%m-%d").strftime("%s")
        point_list.append([int(date) * 1000, point.count])
    return point_list


def get_monthly_stats_points(start_date, end_date, obj_type):
    points = ''
    start_date, end_date = range_date(start_date, end_date)

    if obj_type and start_date and end_date:
        obj_type = obj_type.lower()
        points = MonthlyStats.objects(date__lte=end_date,
                                      date__gte=start_date,
                                      object_type=obj_type)\
            .order_by('timestamp')
    return points


def post_reporter_user(post_id):
    reporters = Report.objects.filter(post_id=post_id)
    user_list = []
    user = {}
    score = 0
    for reporter in reporters:
        user['detail'] = get_simple_user_object(reporter.user.id,
                                                reporter.post.user.id)
        print reporter.user
        user['profile'] = get_profile_data(reporter.user.profile,
                                           reporter.user.id)
        score += reporter.user.profile.score
        user_list.append(user)
    return user_list, score


def get_reported_posts(request):
    before = request.GET.get('before', 0)
    try:
        if before:
            reported_posts = Post.objects\
                .filter(report__gte=1)[before: (before + 1) * 20]
        else:
            reported_posts = Post.objects\
                .filter(report__gte=1)[:20]
    except:
        reported_posts = []
    return reported_posts


def range_date(start, end):
    start_date = None
    end_date = None
    try:
        start = start[:10]
        end = end[:10]

        start_date = datetime.datetime\
            .fromtimestamp(int(start)).strftime("%Y-%m-%d")

        end_date = datetime.datetime\
            .fromtimestamp(int(end)).strftime("%Y-%m-%d")

        if start_date > end_date:
            start_date, end_date = end_date, start_date
    except Exception as e:
        print str(e), "Dashboard tools api range_date error."
    # min_date = datetime.datetime.combine(start_date.date(),
    #                                      start_date.time.min)
    # max_date = datetime.datetime.combine(end_date.date(),
    #                                      end_date.time.max)
    return start_date, end_date


# TO DO
def calculate_post_percent():
    first_step = []
    drilldown, count_of_posts = post_group_by_category()
    first_step = post_group_by_sub_category(count_of_posts)
    return drilldown, first_step, count_of_posts


def ads_group_by(group_by, ended):
    ads = Ad.objects.values(group_by).annotate(cnt_ad=Count(group_by))\
        .filter(ended=ended).order_by('-id')
    return ads


def cnt_post_deleted_by_user(user_id):
    cnt_log = Log.objects\
        .filter(content_type=Log.POST, user=user_id, owner=user_id).count()
    return cnt_log


def cnt_post_deleted_by_admin(user_id):
    cnt_log = Log.objects\
        .filter(content_type=Log.POST, owner=user_id)\
        .exclude(user=user_id).count()
    return cnt_log

# def post_group_by():
#     posts = Post.objects\
#         .values('category', 'category__title', 'category__parent',
#                 'category__parent__title')\
#         .annotate(cnt_post=Count('category')).order_by('-id')
#     return posts


def post_group_by_category():
    count_of_posts = 0
    post_list = []
    data = {}

    post_of_cat = Post.objects.values('category__title', 'category__parent', 'category__parent__title')\
        .annotate(cnt_post=Count('category')).order_by('-id')

    for post in post_of_cat:
        count_of_posts += post['cnt_post']

    for cat in post_of_cat:
        percent = (cat['cnt_post'] * 100) / count_of_posts
        exist_key = data.get(cat['category__parent__title'], False)

        if not exist_key:
            data.update(
                {cat['category__parent__title']: {'name': cat['category__parent__title'],
                                                  'data': [[cat['category__title'], percent]]}})
        else:
            data[cat['category__parent__title']]['data'].append([cat['category__title'], percent])

    post_list.append(data)
    return post_list, count_of_posts


def post_group_by_sub_category(count_of_posts):
    data = []
    post_of_sub_cat = Post.objects\
        .values('category__parent__title')\
        .annotate(cnt_post=Count('category__parent')).order_by('-id')

    for post in post_of_sub_cat:
        post['y'] = (post['cnt_post'] * 100) / count_of_posts
        post['name'] = post['category__parent__title']
        post['drilldown'] = post['category__parent__title']
        try:
            del post['cnt_post']
            del post['category__parent__title']
        except KeyError:
            pass
        data.append(post)
    return data


def get_ads(before, date, ended):
    ads_list = []
    date = datetime.datetime\
        .fromtimestamp(int(date[:10])).strftime("%Y-%m-%d")
    try:
        if before:
            ads = Ad.objects\
                .filter(start__startswith=str(date),
                        ended=ended)[before: (before + 1) * 20]
        else:
            ads = Ad.objects.filter(start__startswith=str(date),
                                    ended=ended)[:20]
    except:
        ads = []

    for ad in ads:
        ad_dict = simple_ad_json(ad)
        ads_list.append(ad_dict)

    return ads_list


def simple_ad_json(ad):
    data = {}
    data['id'] = ad.id
    data['user'] = get_simple_user_object(ad.user_id)
    data['owner'] = get_simple_user_object(ad.owner_id)
    data['ended'] = ad.ended
    data['cnt_view'] = ad.cnt_view
    data['post'] = post_item_json(ad.post)
    data['ads_type'] = ad.ads_type
    data['start'] = ad.start.strftime('%s')
    if ad.end:
        data['end'] = ad.end.strftime('%s')
    else:
        data['end'] = False
    data['ip_address'] = ad.ip_address
    return data


def delete_posts(request):
    import ast
    post_ids = ast.literal_eval(request.POST.get('post_ids'))
    status = False
    if post_ids:

        try:
            posts = Post.objects.filter(id__in=post_ids)
            status = True
        except:
            posts = []

        for post in posts:
            post_after_delete(post=post,
                              user=request.user,
                              ip_address=get_user_ip(request))
            post.delete()
    return status


def undo_report(request):
    post_ids = request.POST.getlist('post_ids')
    status = False
    if post_ids:
        try:
            posts = Post.objects.filter(id__in=post_ids)
            for post in posts:
                post.report = 0
                post.save()
            status = True
        except:
            status = False
    return status


def simple_log_json(obj):
    data = {}
    data['id'] = obj.id
    data['user'] = get_simple_user_object(obj.user_id)
    data['owner'] = get_simple_user_object(obj.owner)
    data['action'] = obj.action
    data['object_id'] = obj.object_id
    data['content_type'] = obj.content_type
    data['text'] = obj.text
    data['create_time'] = obj.create_time.strftime('%s')
    data['post_image'] = obj.post_image
    data['ip_address'] = obj.ip_address
    return data


def get_logs(content_type, action, before):
    data = {}
    if content_type:
        data['content_type'] = int(content_type)

    if action:
        data['action'] = int(action)
    try:
        admin_users = User.objects\
            .filter(is_superuser=True)\
            .values_list('id', flat=True)
        data['user_id__in'] = admin_users

        logs = Log.objects\
            .filter(**data)[before:before + 10]
    except:
        logs = []
    return logs


def get_ads_point(start):
    start = start[:10]
    start_date = datetime.datetime\
        .fromtimestamp(int(start)).strftime("%Y-%m-%d")
    try:
        ads = Ad.objects.filter(start__lte=start_date)\
            .values('start')\
            .annotate(cnt_ads=Count('start')).order_by('id')[:30]
    except:
        ads = []

    return ads


def get_search_log(string, before):
    logs = Log.objects.filter(Q(user__id__iexact=string) |
                              Q(owner__iexact=string) |
                              Q(object_id__iexact=string))[before: before + 10]
    return logs
