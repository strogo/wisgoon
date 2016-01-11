from pin.api6.http import return_json_data, return_un_auth
from pin.views2.dashboard.api.tools import get_monthly_stats_points,\
    check_admin, preparing_chart_points, get_ads_point


def follow_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = str(request.GET.get('start'))[:10]
    end = str(request.GET.get('end'))[:10]

    points = get_monthly_stats_points(start, end, 'follow')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'follow_stats',
                       'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def block_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = str(request.GET.get('start'))[:10]
    end = str(request.GET.get('end'))[:10]

    points = get_monthly_stats_points(start, end, 'block')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'block_stats',
                       'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def like_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = str(request.GET.get('start'))[:10]
    end = str(request.GET.get('end'))[:10]

    points = get_monthly_stats_points(start, end, 'like')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'like_stats',
                       'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def comment_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}
    start = str(request.GET.get('start'))[:10]
    end = str(request.GET.get('end'))[:10]

    points = get_monthly_stats_points(start, end, 'comment')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'comment_stats',
                       'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def bill_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = str(request.GET.get('start'))[:10]
    end = str(request.GET.get('end'))[:10]

    points = get_monthly_stats_points(start, end, 'bill')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'bill_stats',
                       'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def ads_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = request.GET.get('start', '')
    points = get_ads_point(start)

    point_list = []
    for point in points:
        timestamp = point['start'].strftime('%s')
        point_list.append([timestamp, point['cnt_ads']])

    data['objects'] = {'data': point_list,
                       'name': 'ads_stats',
                       'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def join_user_state(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}
    start = str(request.GET.get('start'))[:10]
    end = str(request.GET.get('end'))[:10]

    points = get_monthly_stats_points(start, end, 'user')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'user_stats',
                       'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)
