# -*- coding:utf-8 -*-
import re

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from pin.models import Follow, Block, Likes
from pin.tools import AuthCache
from pin.api6.http import return_bad_request, return_json_data, return_un_auth,\
    return_not_found
from pin.api6.tools import get_next_url, get_simple_user_object, get_int, get_profile_data,\
    update_follower_following, post_item_json

from user_profile.models import Profile
from user_profile.forms import ProfileForm2

from daddy_avatar.templatetags.daddy_avatar import get_avatar

from tastypie.models import ApiKey

from haystack.query import SearchQuerySet
from haystack.query import SQ
from haystack.query import Raw


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
                    'total_count': follow_cnt,
                    'next': ''}

    objects_list = []

    fq = Follow.objects.filter(following_id=user_id)[offset:offset + limit]
    for fol in fq:
        o = {}
        o['user'] = get_simple_user_object(fol.follower_id, cur_user)

        objects_list.append(o)

    data['objects'] = objects_list
    data['meta']['next'] = get_next_url(url_name='api-6-auth-followers',
                                        offset=offset + 20, token=token,
                                        url_args={'user_id': user_id})

    return return_json_data(data)


def following(request, user_id=1):
    data = {}
    objects_list = []
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
                    'total_count': follow_cnt,
                    'next': ''}

    fq = Follow.objects.filter(follower_id=user_id)[offset:offset + limit]
    for fol in fq:
        o = {}
        o['user'] = get_simple_user_object(fol.following_id, cur_user)

        objects_list.append(o)

    data['objects'] = objects_list
    data['meta']['next'] = get_next_url(url_name='api-6-auth-following',
                                        offset=offset + 20,
                                        token=token,
                                        url_args={'user_id': user_id})

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

    username = request.POST.get("username", '')
    password = request.POST.get("password", 'False')
    req_token = request.POST.get("token", '')
    app_token = settings.APP_TOKEN_KEY

    if req_token != app_token:
        data = {
            'status': False,
            'message': _('Application token problem')
        }
        return return_json_data(data)

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
    username = request.POST.get("username", '')
    password = request.POST.get("password", 'False')
    req_token = request.POST.get("token", '')
    email = request.POST.get("email", '')
    app_token = settings.APP_TOKEN_KEY

    if req_token != app_token:
        data = {
            'success': False,
            'message': _('Application token problem')
        }
        return return_json_data(data)

    if not username or not email or not password:
        data = {
            'status': False,
            'message': _('Error in parameters')
        }
        return return_json_data(data)

    if not re.match("^[a-zA-Z0-9_.-]+$", username):
        data = {
            'status': False,
            'message': _('Username bad characters')
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

    if user_id:
        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            return return_not_found()

    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()

    if current_user:
        if Block.objects.filter(user_id=current_user, blocked_id=user_id).count():
            return return_json_data({
                "status": False,
                'message': _('This User Has Blocked You')
            })

    try:
        profile = Profile.objects\
            .only('banned', 'user', 'score', 'cnt_post', 'cnt_like',
                  'website', 'credit', 'level', 'bio').get(user_id=user_id)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user_id=user_id)

    data = {
        'user': get_simple_user_object(user_id, current_user, avatar=210),
        'profile': get_profile_data(profile, user_id)
    }
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

    form = ProfileForm2(request.POST, request.FILES, instance=profile)
    if form.is_valid():
        form.save()
        update_follower_following(profile, current_user)
        msg = 'Your Profile Was Updated'
        status = True
    else:
        msg = form.errors
    return return_json_data({
        'status': status, 'message': msg,
        'profile': get_profile_data(profile, current_user),
        'user': get_simple_user_object(current_user)
    })


def user_search(request):
    row_per_page = 20
    current_user = None
    query = request.GET.get('q', '')
    before = get_int(request.GET.get('before', 0))
    token = request.GET.get('token', '')
    data = {}
    data['meta'] = {'limit': 20, 'next': ""}
    data['objects'] = []

    if query:
        current_user = AuthCache.id_from_token(token=token)

        words = query.split()
        sq = SQ()
        for w in words:
            sq.add(SQ(text__contains=Raw("%s*" % w)), SQ.OR)
            sq.add(SQ(text__contains=Raw(w)), SQ.OR)

        results = SearchQuerySet().models(Profile)\
            .filter(sq)[before:before + row_per_page]

        for result in results:
            result = result.object.user
            o = {}
            if not current_user:
                o['user'] = get_simple_user_object(result.id)
            o['user'] = get_simple_user_object(result.id, current_user)

            data['objects'].append(o)

            data['meta']['next'] = get_next_url(url_name='api-6-post-search',
                                                token=token,
                                                before=before + row_per_page)
        return return_json_data(data)
    else:
        return return_bad_request()


def logout(request):
    auth_logout(request)
    return return_json_data({'status': True, 'message': 'Successfully Logout'})


def user_like(request, user_id):

    user_id = int(user_id)
    current_user_data = None
    post_list = []

    token = request.GET.get('token', '')
    before = get_int(request.GET.get('before', 0))

    data = {}
    data['meta'] = {'limit': 20, 'next': "", 'total_count': 1000}

    if token:
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            return return_un_auth()
        else:
            current_user_data = get_simple_user_object(current_user.id)

    try:
        User.objects.get(id=user_id)
    except User.DoesNotExist:
        return return_not_found()
    try:
        profile = Profile.objects.get(user_id=user_id)
    except:
        profile = Profile.objects.create(user_id=user_id)

    user_likes = Likes.user_likes(user_id=user_id, pid=before)

    for obj in user_likes:
        try:
            if token:
                post_list.append(post_item_json(int(obj), int(current_user.id)))
            else:
                post_list.append(post_item_json(int(obj)))
        except Exception as e:
            print str(e)
    data['latest_items'] = post_list
    data['user'] = get_simple_user_object(user_id)
    data['profile'] = get_profile_data(profile, user_id)
    data['current_user'] = current_user_data
    if post_list:
        data['meta']['next'] = get_next_url(url_name='api-6-auth-user-like',
                                            token=token,
                                            before=post_list[-1]['id'],
                                            url_args={"user_id": user_id})
    return return_json_data(data)


@csrf_exempt
def password_change(request):
    user = None
    token = request.GET.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        return return_un_auth()

    password = request.POST.get('password', '')
    re_password = request.POST.get('re_password', '')
    old_password = request.POST.get('old_password', '')

    if not password or not re_password or not old_password:
        return return_json_data({
            "status": False,
            'message': _('Error in parameters')
        })

    if password != re_password:
        return return_json_data({
            "status": False,
            'message': _('password dismatched')
        })

    u = authenticate(username=user.username, password=old_password)
    if u:
        if not u.is_active:
            return return_json_data({
                "status": False,
                'message': _('password dismatched')
            })
    else:
        return return_json_data({
            "status": False,
            'message': _('Incorrect password.')
        })

    if password == re_password:
        user.set_password(password)
        user.save()
        return return_json_data({
            "status": True,
            'message': _('Password changed')
        })

    return return_json_data({
        "status": False,
        'message': _('Error in parameters')
    })
