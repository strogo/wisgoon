import ast
from django.core.urlresolvers import reverse
from pin.api_tools import abs_url, media_abs_url
from django.contrib.auth.models import User


def get_next_url(url_name, offset=None, token=None, url_args={}, **kwargs):
    n_url_p = reverse(url_name, kwargs=url_args) + "?"
    if offset:
        n_url_p = n_url_p + "offset=%s" % (offset)
    if token:
        n_url_p = n_url_p + "&token=%s" % (token)
    for k, v in kwargs.iteritems():
        n_url_p = n_url_p + "&%s=%s" % (k, v)
    return abs_url(n_url_p)


def category_get_json(cat_id):
    from pin.models import Category
    cat = Category.objects.get(id=cat_id)
    cat_json = {
        'id': cat.id,
        'image': media_abs_url(cat.image.url),
        'title': cat.title,
    }
    return cat_json


def get_int(number):
    try:
        post_id = int(number)
    except ValueError:
        post_id = 0
    return post_id


def get_json(data):
    try:
        to_json = ast.literal_eval(data)
    except ValueError:
        to_json = False
    return to_json


def get_user_data(user_id):
    user_data = {}
    avatar = ''
    try:
        user = User.objects.get(id=user_id)
        user_data['id'] = user.id
        user_data['username'] = user.username
        if user.profile.avatar:
            avatar = str(user.profile.avatar)
        user_data['avatar'] = avatar
    except Exception as e:
        print e
    return user_data
