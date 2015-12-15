from pin.api6.http import return_json_data, return_un_auth
from pin.views2.dashboard.api.tools import get_monthly_stats_points,\
    check_admin, preparing_chart_points


def follow_stats(request):
    if not check_admin(request):
        return return_un_auth()

    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'follow')

    data = {'chart_data': preparing_chart_points(points),
            'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def block_stats(request):
    if not check_admin(request):
        return return_un_auth()

    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'block')

    data = {'chart_data': preparing_chart_points(points),
            'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def like_stats(request):
    if not check_admin(request):
        return return_un_auth()

    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'like')

    data = {'chart_data': preparing_chart_points(points),
            'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def comment_stats(request):
    if not check_admin(request):
        return return_un_auth()

    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'comment')

    data = {'chart_data': preparing_chart_points(points),
            'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)


def bill_stats(request):
    if not check_admin(request):
        return return_un_auth()

    start = str(request.GET.get('start'))
    end = str(request.GET.get('end'))

    points = get_monthly_stats_points(start, end, 'bill')

    data = {'chart_data': preparing_chart_points(points),
            'chart_type': str(request.GET.get('chart_type'))}
    return return_json_data(data)
