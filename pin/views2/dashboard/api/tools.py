# import datetime
from pin.model_mongo import MonthlyStats
from pin.models import Report, Post
from pin.api6.tools import get_simple_user_object, get_profile_data


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
        point_list.append([point.timestamp, point.count])
    return point_list


def get_monthly_stats_points(start_date, end_date, obj_type):
    points = ''
    if obj_type:
        obj_type = obj_type.lower()
        points = MonthlyStats.objects(date__lte=end_date,
                                      date__gte=start_date,
                                      object_type=obj_type).order_by('timestamp')
    return points


def post_reporter_user(post_id):
    reporters = Report.objects.filter(post_id=post_id)
    user_list = []
    user = {}
    for reporter in reporters:
        user['detail'] = get_simple_user_object(reporter.user.id,
                                                reporter.post.user.id)
        user['profile'] = get_profile_data(reporter.user.profile,
                                           reporter.user.id)
        user_list.append(user)
    return user_list


def get_reported_posts():
    try:
        reported_posts = Post.objects.filter(report__gte=1).order_by('-id')
    except:
        reported_posts = []
    return reported_posts


def range_date(start, end):
    import datetime

    start_date = datetime.datetime.strptime(str(start), '%Y-%m-%d')
    end_date = datetime.datetime.strptime(str(end), '%Y-%m-%d')

    if start_date > end_date:
        start_date, end_date = end, start
    # min_date = datetime.datetime.combine(start_date.date(),
    #                                      start_date.time.min)
    # max_date = datetime.datetime.combine(end_date.date(),
    #                                      end_date.time.max)
    return start_date, end_date
