# -*- coding:utf-8 -*-
import re
import hashlib
import urllib2

try:
    import simplejson as json
except ImportError:
    import json

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from pin.models import Follow, Block, Likes, BannedImei, Log, PhoneData, Bills2
from pin.tools import AuthCache, get_user_ip, get_new_access_token
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
        msg = _('Your Profile Was Updated')
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
    return return_json_data({'status': True, 'message': _('Successfully Logout')})


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


@csrf_exempt
def get_phone_data(request):
    if request.method != "POST":
        return return_bad_request()
    os = request.POST.get("os", "")
    app_version = request.POST.get("app_version", "")
    google_token = request.POST.get("google_token", "")
    token = request.POST.get("user_wisgoon_token", None)
    imei = request.POST.get("imei", "")
    android_version = request.POST.get("android_version", "")
    phone_serial = request.POST.get("phone_serial", "")
    phone_model = request.POST.get("phone_model", "")\
        .encode('ascii', 'ignore').decode('ascii')

    if not token:
        return return_un_auth()

    user = AuthCache.user_from_token(token=token)

    if not user:
        return return_un_auth(message=_("user not found"))

    if imei:
        if BannedImei.objects.filter(imei=imei).exists():
            u = User.objects.get(pk=user.id)
            if u.is_active:
                u.is_active = False
                u.save()

                Log.ban_by_imei(actor=user, text=u.username,
                                ip_address=get_user_ip(request))

    try:
        upd = PhoneData.objects.only("hash_data").get(user=user)
        pfields = upd.get_need_fields()

        h_str = '%'.join([str(locals()[f]) for f in pfields])

        hash_str = hashlib.md5(h_str).hexdigest()

        if hash_str == upd.hash_data:
            return return_json_data({
                "status": True,
                'message': _('updated')
            })

    except PhoneData.DoesNotExist:
        pass

    upd, created = PhoneData.objects.get_or_create(user=user)
    upd.imei = imei
    upd.os = os
    upd.phone_model = phone_model
    upd.phone_serial = phone_serial
    upd.android_version = android_version
    upd.app_version = app_version
    upd.google_token = google_token
    upd.logged_out = False
    upd.save()

    return return_json_data({
        "status": True,
        'message': _('accepted')
    })


PACKS = {
    "wisgoon_pack_1": {
        "price": 650,
        "wis": 500
    },
    "wisgoon_pack_2": {
        "price": 1300,
        "wis": 1000
    },
    "wisgoon_pack_3": {
        "price": 2600,
        "wis": 2000
    },
    "wisgoon_pack_4": {
        "price": 6500,
        "wis": 5000
    },
}


# def inc_credit(request):
#     user = None
#     token = request.GET.get('token', '')
#     price = int(request.GET.get('price', 0))
#     baz_token = request.GET.get("baz_token", "")
#     package_name = request.GET.get("package", "")
#     if token:
#         user = AuthCache.user_from_token(token=token)

#     # print user, token, baz_token, package_name

#     if not user or not token or not baz_token or not package_name:
#         return return_not_found(message=_("The parameters entered is incorrect"))

#     if package_name not in PACKS:
#         return return_not_found(message=_("Select a package is not correct"))

#     if PACKS[package_name]['price'] != price:
#         return return_json_data({'status': False,
#                                  'message': _('Price is not right')})

#     # if PACKS[package_name]['price'] == price:
#     if Bills2.objects.filter(trans_id=str(baz_token),
#                              status=Bills2.COMPLETED).count() > 0:
#         b = Bills2()
#         b.trans_id = str(baz_token)
#         b.user = user
#         b.amount = PACKS[package_name]['price']
#         b.status = Bills2.FAKERY
#         b.save()
#         return return_not_found(message=_("bazzar token not right"))
#     else:
#         access_token = get_new_access_token()
#         url = "https://pardakht.cafebazaar.ir/api/validate/ir.mohsennavabi.wisgoon/inapp/%s/purchases/%s/?access_token=%s" % (package_name, baz_token, access_token)
#         try:
#             u = urllib2.urlopen(url).read()
#             j = json.loads(u)

#             if len(j) == 0:
#                 b = Bills2()
#                 b.trans_id = str(baz_token)
#                 b.user = user
#                 b.amount = PACKS[package_name]['price']
#                 b.status = Bills2.NOT_VALID
#                 b.save()
#                 return return_json_data({'status': False,
#                                          'message': 'ex price error'})

#             purchase_state = j.get('purchaseState', None)
#             if purchase_state is None:
#                 return return_json_data({'status': False,
#                                          'message': 'ex price error'})

#             if purchase_state == 0:
#                 b = Bills2()
#                 b.trans_id = str(baz_token)
#                 b.user = user
#                 b.amount = PACKS[package_name]['price']
#                 b.status = Bills2.COMPLETED
#                 b.save()

#                 p = user.profile
#                 p.inc_credit(amount=PACKS[package_name]['wis'])
#             else:
#                 b = Bills2()
#                 b.trans_id = str(baz_token)
#                 b.user = user
#                 b.amount = PACKS[package_name]['price']
#                 b.status = Bills2.NOT_VALID
#                 b.save()
#                 return return_json_data({'status': False,
#                                         'message': 'ex price error'})
#         except Exception:
#             b = Bills2()
#             b.trans_id = str(baz_token)
#             b.user = user
#             b.amount = PACKS[package_name]['price']
#             b.status = Bills2.VALIDATE_ERROR
#             b.save()
#             return return_json_data({'status': False,
#                                     'message': 'ex price error'})

#         return return_json_data({'status': True,
#                                 'message': _('Increased Credit was Successful.')})

#     return return_json_data({'status': False, 'message': 'failed'})
