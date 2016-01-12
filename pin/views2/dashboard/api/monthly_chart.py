from pin.api6.http import return_json_data, return_un_auth, return_bad_request
from pin.views2.dashboard.api.tools import get_monthly_stats_points,\
    check_admin, preparing_chart_points


def follow_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'follow')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'follow_stats',
                       'chart_type': str(request.GET.get('chart_type', "line"))}
    return return_json_data(data)


def block_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'block')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'block_stats',
                       'chart_type': str(request.GET.get('chart_type', "line"))}
    return return_json_data(data)


def like_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'like')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'like_stats',
                       'chart_type': str(request.GET.get('chart_type', "line"))}
    return return_json_data(data)


def comment_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}
    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'comment')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'comment_stats',
                       'chart_type': str(request.GET.get('chart_type', "line"))}
    return return_json_data(data)


def bill_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'bill')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'bill_stats',
                       'chart_type': str(request.GET.get('chart_type', "line"))}
    return return_json_data(data)


def ads_stats(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    start = request.GET.get('start', False)
    end = request.GET.get('end', False)

    if start and end:
        points = get_monthly_stats_points(start, end, 'ads')
    else:
        return return_bad_request()

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'ads_stats',
                       'chart_type': str(request.GET.get('chart_type', "line"))}
    return return_json_data(data)


def join_user_state(request):
    if not check_admin(request):
        return return_un_auth()
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}
    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'user')

    data['objects'] = {'data': preparing_chart_points(points),
                       'name': 'user_stats',
                       'chart_type': str(request.GET.get('chart_type', "line"))}
    return return_json_data(data)
