from pin.api6.http import return_json_data, return_un_auth
from pin.api6.tools import get_next_url
from pin.views2.dashboard.api.tools import simple_log_json, get_logs,\
    check_admin


def show_log(request):
    if not check_admin(request):
        return return_un_auth()

    data = {}
    data['meta'] = {'limit': 20, 'next': '', 'total_count': ''}
    content_type = request.GET.get('content_type', False)
    action = request.GET.get('action', False)
    before = request.GET.get('before', 0)
    logs_list = []

    logs = get_logs(content_type, action, before)
    for log in logs:
        logs_list.append(simple_log_json(log))

    data['objects'] = logs_list

    if len(logs_list) == 20:
        before = int(before) + 20
        token = request.GET.get('token', '')
        data['meta']['next'] = get_next_url(url_name='dashboard-api-log-show',
                                            before=before, token=token)
    return return_json_data(data)
