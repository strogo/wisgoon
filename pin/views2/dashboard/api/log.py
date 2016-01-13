from pin.api6.http import return_json_data, return_un_auth
from pin.api6.tools import get_next_url
from pin.views2.dashboard.api.tools import simple_log_json, get_logs,\
    check_admin, get_search_log


def show_log(request):
    if not check_admin(request):
        return return_un_auth()

    data = {}
    data['meta'] = {'limit': 10, 'next': '', 'previous': '', 'total_count': ''}
    content_type = request.GET.get('content_type', False)
    action = request.GET.get('action', False)
    before = int(request.GET.get('before', 0))
    logs_list = []
    logs = get_logs(content_type, action, before)
    for log in logs:
        logs_list.append(simple_log_json(log))

    data['objects'] = logs_list

    extra_data = {}
    extra_data['url_name'] = 'dashboard-api-log-show'
    extra_data['before'] = before - 10 if before > 0 else "0"
    if action:
        extra_data['action'] = action
    if content_type:
        extra_data['content_type'] = content_type

    data['meta']['previous'] = get_next_url(**extra_data)

    extra_data['before'] = before + 10 if before > 0 else 10
    data['meta']['next'] = get_next_url(**extra_data)
    return return_json_data(data)


def search_log(request):
    string = request.GET.get("q", '')
    before = int(request.GET.get("before", 0))
    data = {}
    data['meta'] = {'limit': 10, 'next': '', 'previous': '', 'total_count': ''}
    result = []

    logs = get_search_log(string, before)
    for log in logs:
        result.append(simple_log_json(log))

    data['objects'] = result
    data['meta']['previous'] = get_next_url(url_name='dashboard-api-log-search',
                                            before=int(before) - 10 if int(before) > 0 else "0",
                                            q=string)

    before = int(before) + 10 if int(before) > 0 else 10
    data['meta']['next'] = get_next_url(url_name='dashboard-api-log-search',
                                        before=before,
                                        q=string)
    return return_json_data(data)
