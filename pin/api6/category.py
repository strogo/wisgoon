from pin.tools import AuthCache
from pin.api6.http import return_json_data, return_un_auth, return_bad_request
from pin.api6.tools import get_int, category_get_json
from pin.api_tools import media_abs_url
from pin.models import Category, SubCategory


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
    category_list = []

    sub_categories = SubCategory.objects.all()
    for category in sub_categories:
        o = {
            "title": category.title,
            "image": media_abs_url(category.image.url),
            "childs": []
        }
        for cat in Category.objects.filter(parent=category):
            o['childs'].append(category_get_json(cat.id))

        category_list.append(o)

    data['objects'] = category_list
    return return_json_data(data)
