# -*- coding: utf-8 -*-
from math import sin, cos, sqrt, atan2, radians

import hashlib
import ast

try:
    import simplejson as json
except ImportError:
    import json

from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from tastypie.models import ApiKey

from pin.tools import AuthCache
from pin.models import Block
from pin.model_mongo import UserLocation
from pin.api_tools import media_abs_url, abs_url

from daddy_avatar.templatetags.daddy_avatar import get_avatar

ROW_PER_PAGE = 20


def get_next_url(url_name, offset, token, **kwargs):
    n_url = reverse(url_name)
    n_url_p = n_url + "?offset=%s" % (offset)
    if token:
        n_url_p = n_url_p + "&token=%s" % (token)
    for k, v in kwargs.iteritems():
        n_url_p = n_url_p + "&%s=%s" % (k, v)
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


R = 6373.0


def calculat_distance(lat1, lon1, lat2, lon2):
    lat1 = radians(float(lat1))
    lon1 = radians(float(lon1))

    lat2 = radians(float(lat2))
    lon2 = radians(float(lon2))

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c
    return "%.1f" % distance


def return_bad_request():
    return HttpResponse('{"reason":"bad request", "status":"400"}',
                        content_type="application/json",
                        status=400)


def return_not_found():
    return HttpResponse('{"reason":"Not found", "status":"404"}',
                        content_type="application/json",
                        status=404)


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
        o['user_name'] = row.user.username
        objects.append(o)

    data['objects'] = objects
    data['meta']['next'] = get_next_url(url_name='api-4-blockers',
                                        offset=offset + 20, token=token)
    return return_json_data(data)


def user_blocked(request):
    print "blocked"
    user, token = check_auth(request)
    if not user:
        return return_un_auth()

    data = {}
    data['meta'] = {'limit': ROW_PER_PAGE,
                    'next': ''}
    objects = []

    offset = int(request.GET.get('offset', 0))
    next_off = offset + 1 * ROW_PER_PAGE

    bq = Block.objects.filter(user_id=user.id)[offset:next_off]
    for row in bq:
        o = {}
        o['user_id'] = row.blocked_id
        o['user_avatar'] = media_abs_url(get_avatar(row.blocked_id, 100))
        o['user_name'] = row.blocked.username
        objects.append(o)

    data['objects'] = objects
    data['meta']['next'] = get_next_url(url_name='api-4-blocked',
                                        offset=offset + 20, token=token)
    return return_json_data(data)


def user_near_by(request):
    user, token = check_auth(request)
    if not user:
        return return_un_auth()

    lat = request.GET.get('lat', None)
    lon = request.GET.get('lon', None)
    if not lat or not lon:
        return return_bad_request()

    data = {}
    data['meta'] = {
        'limit': ROW_PER_PAGE,
        'next': ''
    }
    objects = []

    offset = int(request.GET.get('offset', 0))
    next_off = offset + 1 * ROW_PER_PAGE

    bq = UserLocation.objects(point__near=[lat, lon])[offset:next_off]
    for row in bq:
        if row.user == user.id:
            continue
        user = User.objects.only('username').get(pk=row.user)
        o = {}
        o['user_id'] = user.id
        o['user_avatar'] = media_abs_url(get_avatar(user.id, 100))
        o['user_name'] = user.username
        o['distance'] = calculat_distance(lat1=lat, lon1=lon,
                                          lat2=row.point[0],
                                          lon2=row.point[1])
        objects.append(o)

    data['objects'] = objects
    data['meta']['next'] = get_next_url(url_name='api-4-nearby',
                                        offset=offset + 20, token=token,
                                        **{"lat": lat, "lon": lon})
    return return_json_data(data)


def block_user(request):
    user = None
    token = request.GET.get('token', '')
    user_id = request.GET.get('user_id', None)
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token or not user_id:
        return return_not_found()

    Block.block_user(user_id=user.id, blocked_id=user_id)
    data = {
        "status": "success",
    }
    return return_json_data(data)


def unblock_user(request):
    user = None
    token = request.GET.get('token', '')
    user_id = request.GET.get('user_id', None)
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token or not user_id:
        raise return_not_found()

    Block.unblock_user(user_id=user.id, blocked_id=user_id)
    data = {
        "status": "success",
    }
    return return_json_data(data)


@csrf_exempt
def register(request):
    try:
        data = ast.literal_eval(request.body)
    except SyntaxError:
        return return_bad_request()

    app_token = hashlib.sha1(settings.APP_TOKEN_STR).hexdigest()
    req_token = data.get('token', '')

    if req_token != app_token:
        data = {
            'success': False,
            'reason': 'token problem for register'
        }
        return return_json_data(data)

    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')

    if not username or not email or not password:
        data = {
            'status': False,
            'reason': 'error in parameters'
        }
        return return_json_data(data)

    if User.objects.filter(username=username).exists():
        data = {
            'status': False,
            'reason': u'این نام کاربری قبلا ثبت شده است.'
        }

        return return_json_data(data)

    if User.objects.filter(email=email).exists():
        data = {
            'status': False,
            'reason': u'این ایمیل قبلا استفاده شده است.'
        }
        return return_json_data(data)

    try:
        user = User.objects.create_user(username=username,
                                        email=email,
                                        password=password)
    except:
        data = {
            'status': False,
            'reason': 'error in user creation'
        }
        return return_json_data(data)

    if user:
        data = {
            'status': True,
            'reason': 'user createdsuccessfully'
        }
        return return_json_data(data)
    else:
        data = {
            'status': False,
            'reason': 'problem in create user'
        }
        return return_json_data(data)
