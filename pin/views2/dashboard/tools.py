import datetime

from django.contrib.auth.models import User


def today_range_date():
    today_min = datetime.datetime.combine(datetime.date.today(),
                                          datetime.time.min)
    today_max = datetime.datetime.combine(datetime.date.today(),
                                          datetime.time.max)
    return today_min, today_max


def today_new_user(today_min, today_max):
    cnt_new_users = User.objects\
        .filter(date_joined__range=(today_min, today_max)).count()

    return cnt_new_users
