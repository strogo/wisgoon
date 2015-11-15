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
    try:
        cat = Category.objects.get(id=cat_id)
    except Category.DoesNotExist:
        raise
    else:
        pass
    finally:
        pass
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
            avatar = media_abs_url(str(user.profile.avatar))
        user_data['avatar'] = avatar
    except Exception as e:
        print e
    return user_data


def get_category(cat_id):
    from pin.models import Category
    try:
        cat = Category.objects.get(id=get_int(cat_id))
    except Category.DoesNotExist:
        cat = False
    return cat


def save_post(request, user):
    from django.conf import settings
    from time import time
    from pin.forms import PinDirectForm
    from io import FileIO, BufferedWriter
    from pin.tools import create_filename
    from pin.models import Post

    media_url = settings.MEDIA_ROOT

    model = None
    form = PinDirectForm(request.POST, request.FILES)
    if form.is_valid():
        upload = request.FILES.values()[0]
        filename = create_filename(upload.name)
        try:
            u = "%s/pin/blackhole/images/o/%s" % (media_url, filename)
            with BufferedWriter(FileIO(u, "wb")) as dest:
                for c in upload.chunks():
                    dest.write(c)

            model = Post()
            model.image = "pin/blackhole/images/o/%s" % (filename)
            model.user = user
            model.timestamp = time()
            model.text = form.cleaned_data['description']
            model.category_id = form.cleaned_data['category']
            model.device = 2
            model.save()
            status = True
            msg = 'ok'
        except IOError, e:
            status = False
            msg = str(e)
    else:
        msg = form.errors
        status = False
    return status, msg, model
