# -*- coding:utf-8 -*-
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from pin.models import Follow, Block, Likes
from pin.api7.http import return_bad_request, return_json_data,\
    return_un_auth, return_not_found
from pin.api7.tools import get_next_url, get_simple_user_object, get_int,\
    get_profile_data, update_follower_following, post_item_json,\
    verify_access_token

from user_profile.models import Profile
from user_profile.forms import ProfileForm2

from haystack.query import SearchQuerySet
from haystack.query import SQ
from haystack.query import Raw

# scops = follower_list
def followers(request, user_id):

    token = request.GET.get('token', False)
    cur_user = verify_access_token(token, scopes=['follower_list'])
    if not cur_user:
        return return_un_auth()

    data = {}
    cur_user = None
    follow_cnt = Follow.objects.filter(following_id=user_id).count()

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

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


# scops = follower_list
def following(request, user_id):
    token = request.GET.get('token', False)
    cur_user = verify_access_token(token, scopes=['follower_list'])
    if not cur_user:
        return return_un_auth()

    data = {}
    objects_list = []
    follow_cnt = Follow.objects.filter(follower_id=user_id).count()

    offset = int(request.GET.get('offset', 0))
    limit = int(request.GET.get('limit', 20))

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


# scops = relationships
def follow(request):
    token = request.GET.get('token', False)
    cur_user = verify_access_token(token, scopes=['relationships'])
    if not cur_user:
        return return_un_auth()

    user_id = request.GET.get('user_id', None)

    if not user_id or user_id == cur_user.id:
        return return_bad_request()

    try:
        following = User.objects.get(pk=user_id)
        if not Follow.objects.filter(follower=cur_user,
                                     following=following).exists():
            Follow.objects.create(follower=cur_user, following=following)

    except User.DoesNotExist:
        return return_bad_request()

    data = {
        'status': True,
        'message': _("User followed")
    }
    return return_json_data(data)


# scops = relationships
def unfollow(request):
    token = request.GET.get('token', False)
    cur_user = verify_access_token(token, scopes=['relationships'])
    if not cur_user:
        return return_un_auth()

    user_id = request.GET.get('user_id', None)
    if not user_id or user_id == cur_user.id:
        return return_bad_request()

    try:
        following = User.objects.get(pk=user_id)
        if Follow.objects.filter(follower=cur_user, following=following).exists():
            Follow.objects.filter(follower=cur_user, following=following).delete()

    except User.DoesNotExist:
        return return_bad_request()

    data = {
        'status': True,
        'message': _("User unfollowed")
    }
    return return_json_data(data)


# scops = public_content
def profile(request, user_id):
    token = request.GET.get('token', False)
    current_user = verify_access_token(token, scopes=['public_content'])
    if not current_user:
        return return_un_auth()

    try:
        User.objects.get(id=user_id)
    except User.DoesNotExist:
        return return_not_found()

    if Block.objects.filter(user_id=user_id, blocked_id=current_user).count():
        return return_json_data({
            'message': _('This User Has Blocked You'),
            'status': True
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


# scops = private_content
@csrf_exempt
def update_profile(request):
    token = request.GET.get('token', False)
    current_user = verify_access_token(token, scopes=['private_content'])
    if not current_user:
        return return_un_auth()

    status = False
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


# scops = public_content
def user_search(request):
    token = request.GET.get('token', False)
    current_user = verify_access_token(token, scopes=['public_content'])
    if not current_user:
        return return_un_auth()

    row_per_page = 20
    query = request.GET.get('q', '')
    before = get_int(request.GET.get('before', 0))
    token = request.GET.get('token', '')
    data = {}
    data['meta'] = {'limit': 20, 'next': ""}
    data['objects'] = []

    if query:
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
            o['user'] = get_simple_user_object(result.id, current_user)

            data['objects'].append(o)

            data['meta']['next'] = get_next_url(url_name='api-6-post-search',
                                                token=token,
                                                before=before + row_per_page)
        return return_json_data(data)
    else:
        return return_bad_request()


# scops = public_content
def user_like(request, user_id):
    token = request.GET.get('token', False)
    current_user = verify_access_token(token, scopes=['public_content'])
    if not current_user:
        return return_un_auth()

    post_list = []
    before = get_int(request.GET.get('before', 0))
    data = {}
    data['meta'] = {'limit': 20, 'next': "", 'total_count': 1000}

    try:
        User.objects.get(id=user_id)
    except User.DoesNotExist:
        return return_not_found()

    profile = Profile.objects.get_or_create(user_id=user_id)
    user_likes = Likes.user_likes(user_id=user_id, pid=before)

    for obj in user_likes:
        try:
            post_list.append(post_item_json(int(obj), int(current_user.id)))
        except Exception as e:
            print str(e)
    data['latest_items'] = post_list
    data['user'] = get_simple_user_object(user_id)
    data['profile'] = get_profile_data(profile, user_id)
    data['current_user'] = get_simple_user_object(current_user.id)

    if post_list:
        data['meta']['next'] = get_next_url(url_name='api-6-auth-user-like',
                                            token=token,
                                            before=post_list[-1]['id'],
                                            url_args={"user_id": user_id})
    return return_json_data(data)


# scops = block
@csrf_exempt
def block_user(request, user_id):
    token = request.GET.get('token', False)
    user = verify_access_token(token, scopes=['block'])
    if not user:
        return return_un_auth()
    try:
        User.objects.get(id=user_id)
    except User.DoesNotExist:
        return return_not_found()

    Block.block_user(user_id=user.id, blocked_id=user_id)
    data = {
        'success': True,
        'message': _('User blocked')
    }
    return return_json_data(data)


# scops = block
@csrf_exempt
def unblock_user(request, user_id):
    token = request.GET.get('token', False)
    user = verify_access_token(token, scopes=['block'])
    if not user:
        return return_un_auth()

    if not user or not token:
        return return_un_auth()

    try:
        User.objects.get(id=user_id)
    except User.DoesNotExist:
        return return_not_found()

    Block.unblock_user(user_id=user.id, blocked_id=user_id)
    data = {
        'success': True,
        'message': _('User unblocked')
    }
    return return_json_data(data)
