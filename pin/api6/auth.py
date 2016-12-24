# -*- coding:utf-8 -*-
from __future__ import division
import re
import hashlib
import urllib2
try:
    import simplejson as json
except ImportError:
    import json

from django.conf import settings
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.db.models import Q
from django.http import UnreadablePostError
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login,\
    logout as auth_logout

from user_profile.models import Profile
from user_profile.forms import ProfileForm2

from daddy_avatar.templatetags.daddy_avatar import get_avatar

from tastypie.models import ApiKey

# from haystack.query import SearchQuerySet
# from haystack.query import SQ
# from haystack.query import Raw
from pin.decorators import system_writable
from pin.models import Follow, Block, Likes, BannedImei, PhoneData, Bills2,\
    FollowRequest, VerifyCode
from pin.models_es import ESUsers
from pin.tools import AuthCache, get_new_access_token2
from pin.api6.http import return_bad_request, return_json_data,\
    return_un_auth, return_not_found
from pin.api6.tools import get_next_url, get_simple_user_object,\
    get_int, get_profile_data, update_follower_following, post_item_json,\
    check_user_state, normalize_phone, validate_mobile, get_random_int,\
    code_is_valid, allow_reset


def followers(request, user_id):
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    token = request.GET.get('token', None)
    follow_cnt = Follow.objects.filter(following_id=user_id).count()
    data = {
        'meta': {'limit': limit,
                 'offset': offset,
                 'previous': '',
                 'total_count': follow_cnt,
                 'next': ''},
        'objects': []
    }
    cur_user = None

    status, cur_user = check_user_state(user_id=user_id, token=token)
    if not status:
        return return_json_data(data)

    fq = Follow.objects.filter(following_id=user_id)[offset:offset + limit]
    for fol in fq:
        o = {}
        o['user'] = get_simple_user_object(fol.follower_id, cur_user)

        data['objects'].append(o)

    data['meta']['next'] = get_next_url(url_name='api-6-auth-followers',
                                        offset=offset + 20, token=token,
                                        url_args={'user_id': user_id})

    return return_json_data(data)


def following(request, user_id=1):
    follow_cnt = Follow.objects.filter(follower_id=user_id).count()
    token = request.GET.get('token', None)
    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))
    data = {
        'meta': {'limit': limit,
                 'offset': offset,
                 'previous': '',
                 'total_count': follow_cnt,
                 'next': ''},
        'objects': []
    }

    status, cur_user = check_user_state(user_id=user_id, token=token)
    if not status:
        return return_json_data(data)

    fq = Follow.objects.filter(follower_id=user_id)[offset:offset + limit]
    for fol in fq:
        o = {}
        o['user'] = get_simple_user_object(fol.following_id, cur_user)

        data['objects'].append(o)

    data['meta']['next'] = get_next_url(url_name='api-6-auth-following',
                                        offset=offset + 20,
                                        token=token,
                                        url_args={'user_id': user_id})

    return return_json_data(data)


@system_writable
def follow(request):

    token = request.GET.get('token', '')
    user_id = request.GET.get('user_id', None)
    data = {}

    if token and user_id:
        target_id = get_int(user_id)
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    """ check correct target_id and current user id """
    if target_id == current_user.id:
        return return_bad_request()

    """ Check block status """
    is_blocked = Block.objects.filter(Q(user=current_user,
                                        blocked_id=target_id) |
                                      Q(user_id=target_id,
                                        blocked=current_user)).exists()
    if is_blocked:
        return return_bad_request(message=_("relations is blocked"))

    try:
        target = User.objects.get(pk=target_id)
    except User.DoesNotExist:
        return return_bad_request()

    if target.profile.is_private:
        FollowRequest.objects.get_or_create(user=current_user,
                                            target=target)
        data = {
            'status': True,
            'message': _("Pending follow request")
        }
    else:
        is_followed = Follow.objects\
            .filter(follower=current_user,
                    following=target)\
            .exists()
        if not is_followed:
            Follow.objects.create(follower=current_user,
                                  following=target)

        data = {
            'status': True,
            'message': _("User followed")
        }
    return return_json_data(data)


@system_writable
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
        target = User.objects.get(pk=user_id)
        follow = Follow.objects.get(follower=user, following=target)
        follow.delete()
    except:
        return return_bad_request()

    data = {
        'status': True,
        'message': _("User unfollowed")
    }
    return return_json_data(data)


@system_writable
def remove_follow_req(request):

    token = request.GET.get('token', '')
    user_id = request.GET.get('user_id', None)

    if not token or not user_id:
        return return_bad_request()

    user_id = int(user_id)
    user = AuthCache.user_from_token(token=token)
    if not user:
        return return_un_auth()

    if user_id == user.id:
        return return_bad_request()

    try:
        target = User.objects.get(pk=user_id)
        FollowRequest.objects.filter(user=user,
                                     target=target).delete()
    except:
        return return_bad_request()

    data = {
        'status': True,
        'message': _("User remove follow request")
    }
    return return_json_data(data)


@csrf_exempt
@system_writable
def login(request):

    try:
        username = request.POST.get("username", '')
        password = request.POST.get("password", 'False')
        req_token = request.POST.get("token", '')
    except UnreadablePostError:
        return return_bad_request()

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
@system_writable
def register(request):
    username = request.POST.get("username", '')
    password = request.POST.get("password", 'False')
    req_token = request.POST.get("token", '')
    email = request.POST.get("email", '')
    app_token = settings.APP_TOKEN_KEY

    if req_token != app_token:
        data = {
            'status': False,
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
        api_key, created = ApiKey.objects.get_or_create(user=user)

        data = {
            'status': True,
            'message': _("User created successfully"),
            'user': {
                'token': api_key.key,
                'id': user.id,
                'avatar': get_avatar(user)
            }
        }
        # data = {
        #     'status': True,
        #     'message': _("User created successfully")
        # }
        return return_json_data(data)
    else:
        data = {
            'status': False,
            'message': _("Error in user creation")
        }
        return return_json_data(data)


def profile_name(request, user_name):
    try:
        user = User.objects.only('id').get(username=user_name)
    except User.DoesNotExist:
        return return_not_found()

    return profile(request, user.id)


def profile(request, user_id):
    token = request.GET.get('token', False)
    current_user = None
    current_user_id = None

    if user_id:
        try:
            User.objects.get(id=user_id)
        except User.DoesNotExist:
            return return_not_found()

    if token:
        current_user = AuthCache.user_from_token(token=token)
        if current_user:
            current_user_id = current_user.id

    try:
        profile = Profile.objects\
            .only('banned', 'user', 'score', 'cnt_post', 'cnt_like',
                  'website', 'credit', 'level', 'bio').get(user_id=user_id)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user_id=user_id)

    data = {
        'user': get_simple_user_object(user_id, current_user_id, avatar=210),
        'profile': get_profile_data(profile, user_id)
    }
    return return_json_data(data)


def users_top(request):
    token = request.GET.get('token', False)
    offset = int(request.GET.get('offset', 0))
    limit = 10
    current_user = None

    if token:
        current_user = AuthCache.user_from_token(token=token)

    ob = Profile.objects\
        .only('banned', 'user', 'score', 'cnt_post', 'cnt_like',
              'website', 'credit', 'level', 'bio')\
        .order_by('-score')[offset:offset + limit]
    obj = {
        "meta": {},
        "objects": [],
    }
    if offset > 100:
        return return_json_data(obj)
    tesla = []
    for p in ob:
        if current_user:
            is_blocked = Block.objects\
                .filter(user_id=p.user_id, blocked_id=current_user)\
                .count()
            if is_blocked:
                continue
        data = {
            'user': get_simple_user_object(p.user_id, current_user, avatar=210),
            'profile': get_profile_data(p, p.user_id)
        }
        tesla.append(data)
    obj['objects'] = tesla

    obj['meta']['next'] = get_next_url(url_name='api-6-auth-users-top',
                                       token=token, offset=offset + limit)

    return return_json_data(obj)


@csrf_exempt
@system_writable
def update_profile(request):

    token = request.GET.get('token', False)
    status = False

    if token:
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    profile, create = Profile.objects.get_or_create(user=current_user)

    try:
        form = ProfileForm2(request.POST, request.FILES, instance=profile)
    except UnreadablePostError:
        return return_bad_request()

    if form.is_valid():
        form.save()
        update_follower_following(profile, current_user.id)
        msg = _('Your Profile Was Updated')
        status = True
    else:
        msg = form.errors
    return return_json_data({
        'status': status, 'message': msg,
        'profile': get_profile_data(profile, current_user.id),
        'user': get_simple_user_object(current_user.id)
    })


def user_search(request):
    row_per_page = 10
    current_user = None
    query = request.GET.get('q', '')
    before = get_int(request.GET.get('before', 0))
    token = request.GET.get('token', '')
    data = {}
    data['meta'] = {'limit': 10, 'next': ""}
    data['objects'] = []

    if query:
        current_user = AuthCache.id_from_token(token=token)
        new_from = before + row_per_page

        us = ESUsers()
        try:
            res = us.search(query, from_=before)
        except:
            res = []

        for user in res:
            o = {}
            if not current_user:
                o['user'] = get_simple_user_object(user.id)
            o['user'] = get_simple_user_object(user.id, current_user)

            data['objects'].append(o)
            url_name = 'api-6-auth-user-search'
            data['meta']['next'] = get_next_url(url_name=url_name,
                                                token=token,
                                                before=new_from,
                                                q=query)
        return return_json_data(data)
    else:
        return return_bad_request()


def logout(request):
    auth_logout(request)
    return return_json_data({'status': True,
                             'message': _('Successfully Logout')})


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
@system_writable
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
@system_writable
def get_phone_data(request, startup=None):

    if request.method != "POST":
        return return_bad_request()
    try:
        os = request.POST.get("os", "")
        extra_data = request.POST.get("extra_data", "")
        app_version = request.POST.get("app_version", "")
        google_token = request.POST.get("google_token", "")
        token = request.POST.get("user_wisgoon_token", None)
        imei = request.POST.get("imei", "")
        android_version = request.POST.get("android_version", "")
        phone_serial = request.POST.get("phone_serial", "")
        phone_model = request.POST.get("phone_model", "")\
            .encode('ascii', 'ignore').decode('ascii')
    except UnreadablePostError:
        return return_bad_request()

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

                # Log.ban_by_imei(actor=user, text=u.username,
                #                 ip_address=get_user_ip(request))

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
    upd.extra_data = extra_data
    upd.save()

    if startup:
        return True
    else:
        return return_json_data({
            "status": True,
            'message': _('accepted')
        })


PACKS = {
    "wis_500": {
        "price": 650,
        "wis": 500
    },
    "wis_1000": {
        "price": 1300,
        "wis": 1000
    },
    "wis_2000": {
        "price": 2600,
        "wis": 2000
    },
    "wis_5000": {
        "price": 6500,
        "wis": 5000
    },
}


@csrf_exempt
@system_writable
def inc_credit(request):

    user = None
    token = request.GET.get('token', '')
    price = int(request.POST.get('price', 0))
    baz_token = request.POST.get("baz_token", "")
    package_name = request.POST.get("package", "")

    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token or not baz_token or not package_name:
        message = "The parameters entered is incorrect"
        return return_not_found(message=_(message))

    if package_name not in PACKS:
        return return_not_found(message=_("Select a package is not correct"))

    if PACKS[package_name]['price'] != price:
        return return_json_data({'status': False,
                                 'message': _('Price is wrong')})

    """ If user already use this trans_id """
    if Bills2.objects.filter(trans_id=str(baz_token),
                             status=Bills2.COMPLETED).count() > 0:
        b = Bills2()
        b.trans_id = str(baz_token)
        b.user = user
        b.amount = PACKS[package_name]['price']
        b.status = Bills2.FAKERY
        b.save()
        return return_not_found(message=_("bazzar token not right"))
    else:
        access_token = get_new_access_token2()
        url = "https://pardakht.cafebazaar.ir/api/validate/com.wisgoon.android/inapp/%s/purchases/%s/?access_token=%s" % (
            package_name,
            baz_token,
            access_token)
        try:
            u = urllib2.urlopen(url).read()
            j = json.loads(u)

            if len(j) == 0:
                b = Bills2()
                b.trans_id = str(baz_token)
                b.user = user
                b.amount = PACKS[package_name]['price']
                b.status = Bills2.NOT_VALID
                b.save()
                return return_json_data({'status': False,
                                         'message': 'Not valid purchase data'})

            purchase_state = j.get('purchaseState', None)
            if purchase_state is None:
                message = 'purchase state error request'
                return return_json_data({'status': False,
                                         'message': message})

            if purchase_state == 0:
                b = Bills2()
                b.trans_id = str(baz_token)
                b.user = user
                b.amount = PACKS[package_name]['price']
                b.status = Bills2.COMPLETED
                b.save()

                p = user.profile
                p.inc_credit(amount=PACKS[package_name]['wis'])
            else:
                b = Bills2()
                b.trans_id = str(baz_token)
                b.user = user
                b.amount = PACKS[package_name]['price']
                b.status = Bills2.NOT_VALID
                b.save()

                return return_json_data({'status': False,
                                        'message': 'not valid purchase state'})
        except Exception:
            b = Bills2()
            b.trans_id = str(baz_token)
            b.user = user
            b.amount = PACKS[package_name]['price']
            b.status = Bills2.VALIDATE_ERROR
            b.save()

            message = 'validation error, we correct it later'
            return return_json_data({'status': False,
                                    'message': message})
        message = 'Increased Credit was Successful.'
        return return_json_data({'status': True,
                                'message': _(message)})

    return return_json_data({'status': False, 'message': 'failed'})


@csrf_exempt
@system_writable
def block_user(request, user_id):
    user = None
    token = request.POST.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        return return_un_auth()

    Block.block_user(user_id=user.id, blocked_id=user_id)
    data = {
        'success': True,
        'message': _('User blocked')
    }
    return return_json_data(data)


@csrf_exempt
@system_writable
def unblock_user(request, user_id):
    # TODO implement checking user_id

    user = None
    token = request.POST.get('token', '')
    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        return return_un_auth()

    Block.unblock_user(user_id=user.id, blocked_id=user_id)
    data = {
        'success': True,
        'message': _('User unblocked')
    }
    return return_json_data(data)


@csrf_exempt
@system_writable
def password_reset(request):

    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            email_template = 'registration/password_reset_email_pin.html'
            subject_template = 'registration/password_reset_subject.txt'
            opts = {
                'use_https': request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': None,
                'email_template_name': email_template,
                'subject_template_name': subject_template,
                'request': request,
                'html_email_template_name': None
            }
            form.save(**opts)
            data = {
                'status': True,
                'message': _('Email sent')
            }
            return return_json_data(data)

    return return_bad_request()


@csrf_exempt
@system_writable
def password_reset_2(request):

    if request.method == "POST":
        form = PasswordResetForm(request.POST)

        """Validate email """
        email = request.POST.get('email')
        if not email:
            return return_bad_request(message=_('Email is not correct'),
                                      status=False)

        exist_user = User.objects.filter(email=email).exists()
        if not exist_user:
            msg = _("User account with this email does not exist")
            return return_not_found(message=msg, status=False)

        if form.is_valid():
            email_template = 'registration/password_reset_email_pin.html'
            subject_template = 'registration/password_reset_subject.txt'
            opts = {
                'use_https': request.is_secure(),
                'token_generator': default_token_generator,
                'from_email': None,
                'email_template_name': email_template,
                'subject_template_name': subject_template,
                'request': request,
                'html_email_template_name': None
            }
            form.save(**opts)
            data = {
                'status': True,
                'message': _('Email sent')
            }
            return return_json_data(data)

    return return_bad_request(message=_('Method not allowed'),
                              status=False)


@csrf_exempt
@system_writable
def accept_follow(request):

    data = {}
    token = request.GET.get('token', None)
    user_id = request.POST.get('user_id', None)
    accepted = bool(int(request.POST.get('accepted', 0)))

    if not user_id or not token:
        return return_bad_request()

    target_user = AuthCache.user_from_token(token=token)
    if not target_user:
        return return_un_auth()

    is_req = FollowRequest.objects.filter(user_id=int(user_id),
                                          target=target_user)
    if is_req.exists():
        if accepted:
            Follow.objects.create(follower_id=int(user_id),
                                  following=target_user)
            is_req.delete()
            status = True
            message = 'Allow follow request'
            accepted = 1
        else:
            is_req.delete()
            status = True
            message = 'Decline follow request'
            accepted = 0

        data = {'status': status,
                'message': message,
                'accepted': accepted}
        return return_json_data(data)
    else:
        return return_not_found(message=_("Follow request not exists"))


@system_writable
def follow_requests(request):
    offset = int(request.GET.get('offset', 0))
    limit = 20

    token = request.GET.get('token', None)
    if not token:
        return return_bad_request()

    target_user = AuthCache.user_from_token(token=token)
    if not target_user:
        return return_un_auth()

    fr = FollowRequest.objects\
        .filter(target=target_user)\
        .order_by('-id')[offset:offset + limit]

    data = {
        'meta': {'next': '',
                 'limit': limit,
                 'total_count': len(fr)},
        'objects': []
    }

    for req in fr:
        o = {}
        o['user'] = get_simple_user_object(req.user.id)
        data['objects'].append(o)

    data['meta']['next'] = get_next_url(url_name='api-6-auth-follow-requests',
                                        offset=offset + limit,
                                        token=token
                                        )

    return return_json_data(data)


def create_bill(request):

    # parameters
    token = request.GET.get('token', '')
    price = int(request.POST.get('price', 0))
    package_name = request.POST.get("package", "")

    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token or not package_name:
        message = "The parameters entered is incorrect"
        return return_not_found(message=_(message))

    if package_name not in PACKS:
        return return_not_found(message=_("Select a package is not correct"))

    if PACKS[package_name]['price'] != price:
        return return_json_data({'status': False,
                                 'message': _('Price is wrong')})

    bill = Bills2.objects.create(user=user,
                                 amount=PACKS[package_name]['price'],
                                 status=Bills2.UNCOMPLETED).exists()

    return return_json_data({'status': True,
                             'message': 'Successfully created',
                             'id': bill.id})


@csrf_exempt
@system_writable
def inc_credit_2(request):

    user = None
    token = request.GET.get('token', '')
    baz_token = request.POST.get("baz_token", "")
    price = request.POST.get("price", "")
    bill_id = request.POST.get("bill_id", None)
    package_name = request.POST.get("package", "")
    current_bill = None

    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token or not baz_token or not bill_id:
        message = "The parameters entered is incorrect"
        return return_not_found(message=_(message))

    if package_name not in PACKS:
        return return_not_found(message=_("Select a package is not correct"))

    if PACKS[package_name]['price'] != price:
        return return_json_data({'status': False,
                                 'message': _('Price is wrong')})

    """ Check bill """
    try:
        current_bill = Bills2.objects.get(id=bill_id)
    except:
        return return_not_found(message=_('Bill id is wrong'))

    """ If user already use this trans_id """
    if Bills2.objects.filter(trans_id=str(baz_token),
                             status=Bills2.COMPLETED).count() > 0:

        current_bill.trans_id = str(baz_token)
        current_bill.status = Bills2.FAKERY
        current_bill.save()
        return return_not_found(message=_("bazzar token not right"))
    else:
        access_token = get_new_access_token2()
        url = "https://pardakht.cafebazaar.ir/api/validate/com.wisgoon.android/inapp/%s/purchases/%s/?access_token=%s" % (
            package_name,
            baz_token,
            access_token)
        try:
            u = urllib2.urlopen(url).read()
            j = json.loads(u)

            if len(j) == 0:
                current_bill.trans_id = str(baz_token)
                current_bill.status = Bills2.NOT_VALID
                current_bill.save()
                return return_json_data({'status': False,
                                         'message': 'Not valid purchase data'})

            purchase_state = j.get('purchaseState', None)
            if purchase_state is None:
                message = 'purchase state error request'
                return return_json_data({'status': False,
                                         'message': message})

            if purchase_state == 0:
                current_bill.trans_id = str(baz_token)
                current_bill.status = Bills2.COMPLETED
                current_bill.save()

                p = user.profile
                p.inc_credit(amount=PACKS[package_name]['wis'])
            else:
                current_bill.trans_id = str(baz_token)
                current_bill.status = Bills2.NOT_VALID
                current_bill.save()
                return return_json_data({'status': False,
                                        'message': 'not valid purchase state'})
        except Exception:
            current_bill.trans_id = str(baz_token)
            current_bill.status = Bills2.VALIDATE_ERROR
            current_bill.save()
            message = 'validation error, we correct it later'
            return return_json_data({'status': False,
                                    'message': message})

        message = 'Increased Credit was Successful.'

        return return_json_data({'status': True,
                                'message': _(message)})

    return return_json_data({'status': False, 'message': 'failed'})


@csrf_exempt
def send_code(request):
    phone = request.POST.get('phone', None)
    if not phone:
        return return_bad_request(message=_("Invalid phone number"))

    phone = phone.strip()
    norm_phone = normalize_phone(phone)
    if not validate_mobile(norm_phone):
        return return_bad_request(message=_("Invalid phone number"))
    try:
        profile = Profile.objects.only('phone', 'user').get(phone=norm_phone)
        user_id = profile.user_id
    except:
        return return_not_found(message="User does not exists")

    if not allow_reset(user_id=user_id):
        return return_bad_request(message=_('invalid'))

    code = get_random_int()
    VerifyCode.objects.create(user_id=user_id, code=code)
    # send_sms
    try:
        api_key = ApiKey.objects.get(user_id=user_id)
        token = api_key.key
    except:
        token = None

    data = {
        "message": _("Verification sms sent!"),
        "status": True,
        "token": token
    }

    return return_json_data(data)


@csrf_exempt
def verify_code(request):
    code = request.POST.get('code', None)
    token = request.POST.get('token', None)

    if not code or not token:
        return return_bad_request(message=_("Invalid parameters"))

    user = AuthCache.user_from_token(token=token)
    if not user:
        return return_un_auth()

    user_id = user.id
    if not allow_reset(user_id=user_id):
        return return_bad_request(message=_('invalid'))

    if not code_is_valid(code=code, user_id=user_id):
        return return_bad_request(message=_("Invalid code"))

    message = _('Successfully verify code')
    data = {'status': True,
            'message': message,
            'token': token,
            'code': code}
    return return_json_data(data)


@csrf_exempt
def reset_pass(request):
    password = request.POST.get('password', None)
    token = request.POST.get('token', None)
    code = request.POST.get('code', None)

    if not password or not token or not code:
        return return_bad_request(message=_("Invalid parameters"))

    user = AuthCache.user_from_token(token=token)
    if not user:
        return return_un_auth()

    user_id = user.id
    if not allow_reset(user_id=user_id):
        return return_bad_request(message=_('invalid'))

    if not code_is_valid(code=code, user_id=user_id):
        return return_bad_request(message=_("Invalid code"))

    try:
        user = User.objects.only('password').get(id=user_id)
        user.set_password(password)
    except:
        return return_not_found(message=_("User does not exists"))

    message = _('Successfully reset password')
    data = {'status': True,
            'message': message,
            'token': token}
    return return_json_data(data)
