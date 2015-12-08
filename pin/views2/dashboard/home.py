# from django.shortcuts import render

from pin.api6.http import return_json_data
from pin.views2.dashboard.tools import today_range_date, today_new_user


def home(request):
    data = {}
    today_min, today_max = today_range_date()

    data['new_users'] = {'cnt_new_users': today_new_user(today_min, today_max),
                         'more_info': 'url'}
    return return_json_data(data)
    # return render(request, 'dashboard/home.html', {'cnt_new_users': new_users})
