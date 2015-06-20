try:
    import simplejson as json
except ImportError:
    import json

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from tastypie.models import ApiKey

from pin.tools import AuthCache
from pin.models import Block
from pin.api_tools import media_abs_url, abs_url

from daddy_avatar.templatetags.daddy_avatar import get_avatar

ROW_PER_PAGE = 20


def get_next_url(url_name, offset, token):
    n_url = reverse(url_name)
    n_url_p = n_url + "?offset=%s" % (offset)
    if token:
        n_url_p = n_url_p + "&token=%s" % (token)
    return abs_url(n_url_p)


def check_auth(request):
    token = request.GET.get('token', '')
    if not token:
        return False, token

    try:
        user = AuthCache.user_from_token(token)
        if not user:
            return False, token
        user._ip = request.META.get("REMOTE_ADDR", '127.0.0.1')

        if not user.is_active:
            return False, token
        else:
            return user, token
    except ApiKey.DoesNotExist:
        return False, token

    return False, token


def return_un_auth():
    return HttpResponse('{"reason":"authentication faild", "status":"403"}',
                        content_type="application/json",
                        status=403)


def return_json_data(data):
    return HttpResponse(json.dumps(data), content_type='application/json')


def user_blockers(request):
    user, token = check_auth(request)
    if not user:
        return return_un_auth()

    data = {}
    data['meta'] = {'limit': ROW_PER_PAGE,
                    'next': ''}
    objects = []

    offset = int(request.GET.get('offset', 0))
    next_off = offset + 1 * ROW_PER_PAGE

    bq = Block.objects.filter(blocked_id=user.id)[offset:next_off]
    for row in bq:
        o = {}
        o['user_id'] = row.user_id
        o['user_avatar'] = media_abs_url(get_avatar(row.user_id, 100))
        objects.append(o)

    data['objects'] = objects
    data['meta']['next'] = get_next_url(url_name='api-4-blockers',
                                        offset=offset + 20, token=token)
    return return_json_data(data)
