# import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import UnreadablePostError
from django.utils.translation import ugettext as _

from pin.models import Post
from pin.models_redis import LikesRedis
from pin.decorators import system_writable
from pin.tools import AuthCache, get_post_user_cache
from pin.api6.tools import get_int, get_simple_user_object, get_next_url,\
    check_user_state
from pin.api6.http import return_json_data, return_not_found, return_un_auth,\
    return_bad_request

from django.conf import settings
import requests
import json


@system_writable
def like_post(request, item_id):

    token = request.GET.get('token', False)

    try:
        post = get_post_user_cache(post_id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    if token:
        status, current_user_id = check_user_state(user_id=post.user_id,
                                                   token=token)
        if not current_user_id or not status:
            return return_un_auth()
    else:
        return return_bad_request()
    like, dislike, current_like = LikesRedis(post_id=item_id)\
        .like_or_dislike(user_id=current_user_id,
                         post_owner=post.user_id,
                         category=post.category_id,
                         date=post.timestamp)

    if like:
        user_act = 1
        user = get_simple_user_object(current_user_id, post.user_id)
    elif dislike:
        user_act = -1
        user = {}

    data = {'cnt_like': current_like, 'user_act': user_act, 'user': user}
    return return_json_data(data)


@csrf_exempt
@system_writable
def like_item(request):

    data = {}
    try:
        token = request.POST.get('token', False)
        item_id = int(request.POST.get('item_id', 0))
    except UnreadablePostError:
        return return_bad_request()

    if settings.DEBUG:
        url = "http://127.0.0.1:8801/v7/like/item/?token={}"
    else:
        url = "http://api.wisgoon.com/v7/like/item/?token={}"

    url = url.format(token)
    payload = {}
    payload['item_id'] = item_id

    # Get choices post
    s = requests.Session()
    res = s.post(url, data=payload, headers={'Connection': 'close'})

    if res.status_code != 200:
        return return_bad_request(status=False)

    try:
        data = json.loads(res.content)
    except:
        return return_bad_request()

    # try:
    #     token = request.POST.get('token', False)
    #     item_id = int(request.POST.get('item_id', 0))
    # except UnreadablePostError:
    #     return return_bad_request()

    # try:
    #     post = get_post_user_cache(post_id=get_int(item_id))
    # except Post.DoesNotExist:
    #     return return_not_found()

    # if token:
    #     # current_user = AuthCache.user_from_token(token=token)
    #     status, current_user_id = check_user_state(user_id=post.user_id,
    #                                                token=token)
    #     if not current_user_id or not status:
    #         msg = _('You do not have access to this post')
    #         return return_un_auth(message=msg)

    # else:
    #     return return_bad_request()

    # like, dislike, current_like = LikesRedis(post_id=item_id)\
    #     .like_or_dislike(user_id=current_user_id,
    #                      post_owner=post.user_id,
    #                      category=post.category_id,
    #                      date=post.timestamp)

    # if like:
    #     user_act = 1
    #     user = get_simple_user_object(current_user_id, post.user_id)
    # elif dislike:
    #     user_act = -1
    #     user = {}

    # data = {'cnt_like': current_like, 'user_act': user_act, 'user': user}
    return return_json_data(data)


def post_likers(request, item_id):

    data = {}
    data['objects'] = []
    data['meta'] = {'limit': 20, 'next': '', 'total_count': 1000}
    payload = {}
    before = request.GET.get('before', 0)
    token = request.GET.get('token', False)

    if token:
        payload['token'] = token
    if before:
        payload['before'] = before

    if settings.DEBUG:
        url = "http://127.0.0.1:8801/v7/like/likers/post/{}/"
    else:
        url = "http://api.wisgoon.com/v7/like/likers/post/{}/"
    url = url.format(item_id)

    # Get choices post
    s = requests.Session()
    res = s.get(url, params=payload, headers={'Connection': 'close'})

    if res.status_code == 200:
        try:
            data = json.loads(res.content)
        except:
            pass

    if data['objects']:
        data['meta']['next'] = get_next_url(url_name='api-6-likers-post',
                                            token=token,
                                            before=int(before) + 20,
                                            url_args={"item_id": item_id})

    # data = {}
    # current_user_id = None
    # data['meta'] = {'limit': 20,
    #                 'next': '',
    #                 'total_count': LikesRedis(post_id=item_id).cntlike()}
    # likers_list = []
    # before = request.GET.get('before', False)

    # token = request.GET.get('token', False)
    # if token:
    #     current_user_id = AuthCache.id_from_token(token=token)
    #     # if current_user:
    #     #     current_user_id = current_user.id

    # if not before:
    #     before = 0

    # try:
    #     post = get_post_user_cache(post_id=get_int(item_id))
    # except Post.DoesNotExist:
    #     return return_not_found()

    # if before:
    #     likers = LikesRedis(post_id=post.id)\
    #         .get_likes(offset=get_int(before), limit=20, as_user_object=False)
    # else:
    #     likers = LikesRedis(post_id=post.id)\
    #         .get_likes(offset=0, limit=20, as_user_object=False)

    # for user in likers:
    #     try:
    #         u = {
    #             'user': get_simple_user_object(int(user), current_user_id)
    #         }
    #         likers_list.append(u)
    #     except Exception as e:
    #         print str(e)

    # data['objects'] = likers_list
    # if data['objects']:
    #     data['meta']['next'] = get_next_url(url_name='api-6-likers-post',
    #                                         token=token,
    #                                         before=int(before) + 20,
    #                                         url_args={"item_id": item_id})
    return return_json_data(data)
