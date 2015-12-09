# import datetime

from pin.model_mongo import MonthlyStats


# def today_range_date():
#     today_min = datetime.datetime.combine(datetime.date.today(),
#                                           datetime.time.min)
#     today_max = datetime.datetime.combine(datetime.date.today(),
#                                           datetime.time.max)
#     return today_min, today_max


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
