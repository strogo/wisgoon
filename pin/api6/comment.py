from pin.tools import AuthCache
from pin.api6.http import return_json_data, return_bad_request, return_not_found

from pin.models import Comments


def comment_post(request, item_id):
    data = {}
    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': 1000}

    before = request.GET.get('before', None)

    if not before:
        before = 0

    data['objects'] = {}

    o = []
    for com in Comments.objects.filter(object_pk=item_id):
        o2 = {}
        o2['id'] = com.id
        o2['comment'] = com.comment
        o.append(o2)

    data['objects'] = o

    return return_json_data(data)
