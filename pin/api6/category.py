from pin.tools import AuthCache
from pin.api6.http import return_json_data, return_un_auth, return_bad_request
from pin.api6.tools import get_int, get_next_url, category_get_json
from pin.models import Category


def show_category(request, cat_id):
    token = request.GET.get('token', False)
    data = {}
    data['meta'] = {'limit': 1, 'next': '', 'total_count': 1}
    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    data['objects'] = [category_get_json(get_int(cat_id))]
    return return_json_data(data)


def all_category(request):
    data = {}
    data['meta'] = {'limit': 20, 'next': '', 'total_count': 1000}
    token = request.GET.get('token', '')
    before = request.GET.get('before', '')
    category_list = []

    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()
    if before:
        categories = Category.objects.filter(id__lt=before).order_by('-id')[:10]
    else:
        categories = Category.objects.order_by('-id')[:10]

    for category in categories:
        category_list.append(category_get_json(category.id))

    data['objects'] = category_list
    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-categoreis',
                                            before=last_item,
                                            )
    return return_json_data(data)
