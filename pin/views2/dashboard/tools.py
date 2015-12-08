# import datetime

from pin.model_mongo import MonthlyStats


# def today_range_date():
#     today_min = datetime.datetime.combine(datetime.date.today(),
#                                           datetime.time.min)
#     today_max = datetime.datetime.combine(datetime.date.today(),
#                                           datetime.time.max)
#     return today_min, today_max


def today_new_users(today):
    cnt_today_users = MonthlyStats.objects\
        .filter(date=(today), object_type=MonthlyStats.USER).count()

    return cnt_today_users


def today_new_posts(today):
    cnt_today_posts = MonthlyStats.objects\
        .filter(date=today, object_type=MonthlyStats.POST).count()

    return cnt_today_posts


def today_likes(today):
    cnt_today_likes = MonthlyStats.objects\
        .filter(date=today, object_type=MonthlyStats.LIKE).count()

    return cnt_today_likes


def today_blocks(today):
    cnt_today_blocks = MonthlyStats.objects\
        .filter(date=today, object_type=MonthlyStats.BLOCK).count()

    return cnt_today_blocks


def today_follow(today):
    cnt_today_follow = MonthlyStats.objects\
        .filter(date=today, object_type=MonthlyStats.FOLLOW).count()

    return cnt_today_follow


def today_view_pages(today):
    today_view = MonthlyStats.objects\
        .filter(date=today, object_type=MonthlyStats.VIEW).count()
    return today_view


def today_bills(today):
    today_cnt_bills = MonthlyStats.objects\
        .filter(date=today, object_type=MonthlyStats.BILL).count()
    return today_cnt_bills


def today_comments(today):
    today_cnt_bills = MonthlyStats.objects\
        .filter(date=today, object_type=MonthlyStats.COMMENT).count()
    return today_cnt_bills
