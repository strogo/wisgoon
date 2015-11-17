# -*- coding:utf-8 -*-
import ast

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from tastypie.models import ApiKey
from user_profile.forms import ProfileForm
from pin.api6.http import return_bad_request, return_json_data, return_un_auth
from pin.api6.tools import get_next_url, get_user_data, get_int, get_profile_data,\
    update_follower_following
from pin.tools import AuthCache
from pin.models import Follow, Block
from user_profile.models import Profile
from pin.cacheLayer import UserDataCache
# from daddy_avatar.templatetags import daddy_avatar
from daddy_avatar.templatetags.daddy_avatar import get_avatar
from haystack.query import SearchQuerySet


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
        u['username'] = UserDataCache.get_user_name(fol.follower_id)
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
        u['username'] = UserDataCache.get_user_name(fol.following_id)

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

    if token and user_id:
        user_id = get_int(user_id)
        user = AuthCache.user_from_token(token=token)
        if not user:
            return return_un_auth()
    else:
        return return_bad_request()

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

    if token and user_id:
        user_id = get_int(user_id)
        user = AuthCache.user_from_token(token=token)
        if not user:
            return return_un_auth()
    else:
        return return_bad_request()

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


def profile(request, user_id):
    token = request.GET.get('token', False)
    current_user = None

    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()

    if current_user:
        if Block.objects.filter(user_id=current_user, blocked_id=user_id).count():
            return return_json_data({})

        follow_status = Follow.objects.filter(follower=current_user,
                                              following=user_id).count()
    else:
        follow_status = None

    try:
        profile = Profile.objects.only('banned', 'user', 'score', 'cnt_post', 'cnt_like', 'website', 'credit', 'level', 'bio').get(user_id=user_id)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user_id=user_id)

    data = {'user': get_user_data(user_id),
            'profile': get_profile_data(profile, user_id),
            'follow_status': follow_status}
    return return_json_data(data)


@csrf_exempt
def update_profile(request):
    token = request.GET.get('token', False)
    status = False

    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    profile, create = Profile.objects.get_or_create(user=current_user)

    form = ProfileForm(request.POST, request.FILES, instance=profile)
    if form.is_valid():
        form.save()
        update_follower_following(profile, current_user)
        msg = 'Your Profile Was Updated'
        status = True
    else:
        msg = form.errors
        msg = 'Error'
    return return_json_data({'status': status, 'message': msg,
                             'profile': get_profile_data(profile, current_user),
                             'user': get_user_data(current_user)})


def user_search(request):
    row_per_page = 20
    current_user = None
    query = request.GET.get('q', '')
    offset = get_int(request.GET.get('offset', 0))
    token = request.GET.get('token', '')
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}
    results = SearchQuerySet().models(Profile)\
        .filter(content__contains=query)[offset:offset + 1 * row_per_page]

    if query and token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()

        data['objects'] = []
        for result in results:
            print result
            result = result.object
            print result

            o = {}
            o['id'] = result.id
            o['avatar'] = get_avatar(result.id, 100)
            o['username'] = result.user.username
            try:
                o['name'] = result.name
            except:
                o['name'] = ""

            if current_user:
                o['follow_by_user'] = Follow\
                    .get_follow_status(follower=current_user, following=result.id)
            else:
                o['follow_by_user'] = False

            data['objects'].append(o)
        return return_json_data(data)
    else:
        return return_bad_request()
