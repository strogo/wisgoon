# -*- coding:utf-8 -*-
import ast

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from tastypie.models import ApiKey

from pin.api5.http import return_bad_request, return_json_data, return_un_auth
from pin.api5.tools import get_next_url
from pin.tools import AuthCache
from pin.models import Follow
from pin.cacheLayer import UserNameCache

# from daddy_avatar.templatetags import daddy_avatar
from daddy_avatar.templatetags.daddy_avatar import get_avatar


def followers(request, user_id):
    data = {}
    cur_user = None
    follow_cnt = Follow.objects.filter(following_id=user_id).count()

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    token = request.GET.get('token', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    data['meta'] = {'limit': limit,
                    'offset': offset,
                    'previous': '',
                    'total_count': follow_cnt}

    data['meta']['next'] = get_next_url(url_name='api-5-auth-followers',
                                        offset=offset + 20, token=token,
                                        url_args={'user_id': user_id})

    objects_list = []

    fq = Follow.objects.filter(following_id=user_id)[offset:offset + limit]
    for fol in fq:
        o = {}
        u = {}
        u['id'] = fol.follower_id
        u['avatar'] = get_avatar(fol.follower_id, size=100)
        u['username'] = UserNameCache.get_user_name(fol.follower_id)
        o['user'] = u
        if cur_user:
            o['follow_by_user'] = Follow.objects\
                .filter(follower_id=cur_user, following_id=fol.follower_id)\
                .exists()
        else:
            o['follow_by_user'] = False

        objects_list.append(o)

    data['objects'] = objects_list

    return return_json_data(data)


def following(request, user_id=1):
    data = {}
    cur_user = None
    follow_cnt = Follow.objects.filter(follower_id=user_id).count()

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

    token = request.GET.get('token', '')
    if token:
        cur_user = AuthCache.id_from_token(token=token)

    data['meta'] = {'limit': limit,
                    'offset': offset,
                    'previous': '',
                    'total_count': follow_cnt}

    objects_list = []

    data['meta']['next'] = get_next_url(url_name='api-5-auth-following',
                                        offset=offset + 20, token=token,
                                        url_args={'user_id': user_id})

    fq = Follow.objects.filter(follower_id=user_id)[offset:offset + limit]
    for fol in fq:
        o = {}
        u = {}
        u['id'] = fol.following_id
        u['avatar'] = get_avatar(fol.following_id, size=100)
        u['username'] = UserNameCache.get_user_name(fol.following_id)

        o['user'] = u

        if cur_user:
            o['follow_by_user'] = Follow.objects\
                .filter(follower_id=cur_user, following_id=fol.following_id)\
                .exists()
        else:
            o['follow_by_user'] = False

        objects_list.append(o)

    data['objects'] = objects_list

    return return_json_data(data)


def follow(request):
    token = request.GET.get('token', '')
    user_id = request.GET.get('user_id', None)

    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not user_id:
        return return_un_auth()

    user_id = int(user_id)

    if user_id == user.id:
        return return_bad_request()

    try:
        following = User.objects.get(pk=user_id)
        if not Follow.objects.filter(follower=user,
                                     following=following).exists():
            Follow.objects.create(follower=user, following=following)

    except User.DoesNotExist:
        return return_bad_request()

    data = {
        'status': True,
        'message': _("User followed")
    }
    return return_json_data(data)


def unfollow(request):
    token = request.GET.get('token', '')
    user_id = request.GET.get('user_id', None)

    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not user_id:
        return return_un_auth()
    user_id = int(user_id)

    if user_id == user.id:
        return return_bad_request()

    try:
        following = User.objects.get(pk=user_id)
        if Follow.objects.filter(follower=user, following=following).exists():
            Follow.objects.filter(follower=user, following=following).delete()

    except User.DoesNotExist:
        return return_bad_request()

    data = {
        'status': True,
        'message': _("User unfollowed")
    }
    return return_json_data(data)


@csrf_exempt
def login(request):
    try:
        data = ast.literal_eval(request.body)
    except SyntaxError:
        return return_bad_request()

    app_token = settings.APP_TOKEN_KEY
    req_token = data.get('token', '')

    if req_token != app_token:
        data = {
            'status': False,
            'message': _('Application token problem')
        }
        return return_json_data(data)

    username = data.get('username', '')
    password = data.get('password', '')

    user = authenticate(username=username, password=password)

    if user:
        if user.is_active:
            auth_login(request, user)

            api_key, created = ApiKey.objects.get_or_create(user=user)

            data = {
                'status': True,
                'message': _('Login successfully'),
                'user': {
                    'token': api_key.key,
                    'id': user.id,
                    'avatar': get_avatar(user)
                }
            }
            return return_json_data(data)

        else:
            data = {
                'status': False,
                'message': _("User is not active")
            }
            return return_json_data(data)
    else:
        data = {
            'status': False,
            'message': _("Username or password not valid")
        }
        return return_json_data(data)


@csrf_exempt
def register(request):
    try:
        data = ast.literal_eval(request.body)
    except SyntaxError:
        return return_bad_request()

    app_token = settings.APP_TOKEN_KEY
    req_token = data.get('token', '')

    if req_token != app_token:
        data = {
            'success': False,
            'message': _('Application token problem')
        }
        return return_json_data(data)

    username = data.get('username', '')
    email = data.get('email', '')
    password = data.get('password', '')

    if not username or not email or not password:
        data = {
            'status': False,
            'message': _('Error in parameters')
        }
        return return_json_data(data)

    if User.objects.filter(username=username).exists():
        data = {
            'status': False,
            'message': _('Username already exists')
        }

        return return_json_data(data)

    if User.objects.filter(email=email).exists():
        data = {
            'status': False,
            'message': _('Email already exists')
        }
        return return_json_data(data)

    try:
        user = User.objects.create_user(username=username,
                                        email=email,
                                        password=password)
    except:
        data = {
            'status': False,
            'message': _("Error in user creation")
        }
        return return_json_data(data)

    if user:
        data = {
            'status': True,
            'message': _("User created successfully")
        }
        return return_json_data(data)
    else:
        data = {
            'status': False,
            'message': _("Error in user creation")
        }
        return return_json_data(data)
