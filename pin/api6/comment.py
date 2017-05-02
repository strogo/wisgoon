from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.http import UnreadablePostError

from pin.tools import AuthCache
from pin.models import Comments, Post, Follow
from pin.api6.tools import get_int, get_next_url,\
    get_comments, comment_objects_list, comment_item_json
from pin.api6.http import return_json_data, return_not_found, return_un_auth,\
    return_bad_request
from pin.tools import check_block, get_post_user_cache
from pin.toolkit import check_auth
from pin.decorators import system_writable

from django.conf import settings
import requests
import json


def comment_post(request, item_id):

    limit = 20
    data = {}
    data['objects'] = {}
    data['meta'] = {'limit': limit, 'next': '', 'total_count': 1000}
    before = int(request.GET.get('before', 0))

    if settings.DEBUG:
        url = "http://127.0.0.1:8801/v7/comment/post/{}/"
    else:
        url = "http://test.wisgoon.com/v7/comment/post/{}/"

    url = url.format(item_id)
    payload = {}
    payload['before'] = before

    # Get choices post
    s = requests.Session()
    res = s.get(url, params=payload, headers={'Connection': 'close'})

    if res.status_code == 200:
        try:
            data = json.loads(res.content)
        except:
            pass

    if data:
        data['meta']['next'] = get_next_url(url_name='api-6-comment-post',
                                            before=before + limit,
                                            url_args={"item_id": item_id}
                                            )

    # limit = 20
    # data = {}
    # data['objects'] = {}
    # data['meta'] = {'limit': limit, 'next': '', 'total_count': 1000}
    # before = int(request.GET.get('before', 0))

    # comments = get_comments(item_id, limit, before)
    # data['objects'] = comment_objects_list(comments)

    # if data:
    #     data['meta']['next'] = get_next_url(url_name='api-6-comment-post',
    #                                         before=before + limit,
    #                                         url_args={"item_id": item_id}
    #                                         )
    return return_json_data(data)


@csrf_exempt
@system_writable
def add_comment(request, item_id):

    data = {}
    token = request.GET.get('token', None)
    comment = request.POST.get('comment', None)

    if not token:
        return return_json_data({
            'status': False,
            'message': _('error in user validation')
        })

    if settings.DEBUG:
        url = "http://127.0.0.1:8801/v7/comment/add/post/{}/?token={}"
    else:
        url = "http://test.wisgoon.com/v7/comment/add/post/{}/?token={}"

    url = url.format(item_id, token)
    payload = {}
    payload['comment'] = comment

    # Get choices post
    s = requests.Session()
    res = s.post(url, data=payload, headers={'Connection': 'close'})

    if res.status_code != 200:
        return return_bad_request(status=False)

    try:
        data = json.loads(res.content)
    except:
        pass

    return return_json_data(data)

    # user = check_auth(request)
    # if not user:
    #     return return_json_data({
    #         'status': False,
    #         'message': _('error in user validation')
    #     })

    # try:
    #     post = get_post_user_cache(post_id=get_int(item_id))
    #     # post = Post.objects.get(id=get_int(item_id))
    # except Post.DoesNotExist:
    #     return return_not_found(status=False)

    # try:
    #     text = request.POST.get('comment', False)
    # except UnreadablePostError:
    #     return return_bad_request()

    # if not text:
    #     return return_json_data({
    #         'status': False,
    #         'message': _('Please Enter Your Comment')
    #     })

    # if user.id != post.user.id:
    #     if check_block(user_id=post.user_id, blocked_id=user.id):
    #         return return_json_data({
    #             'status': False,
    #             'message': _('This User Has Blocked You')
    #         })

    #     if post.user.profile.is_private:
    #         is_follow = Follow.objects\
    #             .filter(follower_id=user.id,
    #                     following_id=post.user_id)\
    #             .exists()
    #         if not is_follow:
    #             return return_json_data({
    #                 'status': False,
    #                 'message': _('Unsuccessfully was Create Comment.')
    #             })

    # try:
    #     comment = Comments.objects.create(object_pk=post, comment=text,
    #                                       user_id=get_int(user.id),
    #                                       ip_address=user._ip)
    #     comment_data = comment_item_json(comment)
    #     comment_data['status'] = True
    #     comment_data['message'] = _('Successfully was Create Comment.')
    #     return return_json_data(comment_data)
    # except:
    #     return return_json_data({
    #         'status': False,
    #         'message': _('Unsuccessfully was Create Comment.')
    #     })


@system_writable
def delete_comment(request, comment_id):

    data = {}
    token = request.GET.get('token', None)

    if not token:
        return return_json_data({
            'status': False,
            'message': _('error in user validation')
        })

    if settings.DEBUG:
        url = "http://127.0.0.1:8801/v7/comment/delete/{}/?token={}"
    else:
        url = "http://test.wisgoon.com/v7/comment/delete/{}/?token={}"

    url = url.format(comment_id, token)

    # Get choices post
    s = requests.Session()
    res = s.get(url, headers={'Connection': 'close'})

    if res.status_code != 200:
        return return_bad_request(status=False)

    try:
        data = json.loads(res.content)
    except:
        pass

    if data["status"]:
        data["comment_id"] = data["id"]
    return return_json_data(data)

    # user = check_auth(request)
    # if not user:
    #     return return_json_data({
    #         'status': False,
    #         'message': _('error in user validation')
    #     })

    # try:
    #     comment = Comments.objects.get(id=get_int(comment_id))
    # except Comments.DoesNotExist:
    #     return return_json_data({
    #         'status': False,
    #         'message': _('comment not found')
    #     })

    # if comment.user_id == user.id or comment.object_pk.user.id == user.id:
    #     comment_id = comment.id
    #     comment.delete()
    #     data = {
    #         'status': True,
    #         'message': _('Successfully Removed Comment'),
    #         'comment_id': comment_id
    #     }
    # else:
    #     data = {
    #         'status': False,
    #         'message': _('Access Denied')
    #     }

    # return return_json_data(data)


@csrf_exempt
@system_writable
def delete_comments(request):

    data = {}
    token = request.GET.get('token', None)
    comment_ids = request.POST.get("comment_id", None)

    if not comment_ids:
        return return_bad_request()

    if not token:
        return return_json_data({
            'status': False,
            'message': _('error in user validation')
        })

    if settings.DEBUG:
        url = "http://127.0.0.1:8801/v7/comment/list/remove/?token={}"
    else:
        url = "http://test.wisgoon.com/v7/comment/list/remove/?token={}"

    url = url.format(token)
    payload = {}
    payload['comment_id'] = comment_ids

    # Get choices post
    s = requests.Session()
    res = s.post(url, data=payload, headers={'Connection': 'close'})

    if res.status_code != 200:
        return return_bad_request(status=False)

    try:
        data = json.loads(res.content)
    except:
        pass

    return return_json_data(data)

    # comment_ids = request.POST.get("comment_id", None)
    # if not comment_ids:
    #     return return_bad_request()

    # comment_ids = comment_ids.split(",")
    # if not comment_ids:
    #     return return_bad_request()

    # removed_list = []

    # user = check_auth(request)
    # if not user:
    #     return return_un_auth()

    # for comment_id in comment_ids:
    #     try:
    #         comment = Comments.objects.get(id=int(comment_id))
    #     except Comments.DoesNotExist:
    #         continue

    #     if comment.user_id == user.id or comment.object_pk.user.id == user.id:
    #         comment_id = comment.id
    #         comment.delete()
    #         removed_list.append(comment_id)
    #     else:
    #         continue

    # data = {
    #     'comment_id': removed_list
    # }
    # return return_json_data(data)


@csrf_exempt
@system_writable
def report(request, comment_id):
    token = request.GET.get('token', '')
    if token:
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    if comment_id and Comments.objects.filter(pk=comment_id).exists():
        Comments.objects.filter(pk=comment_id).update(reported=True)
        data = {
            'status': True,
            'message': _('Comment reported'),
            'comment_id': comment_id
        }
        return return_json_data(data)
    else:
        data = {
            'status': False,
            'message': _('Comment not exists'),
            'comment_id': comment_id
        }
        return return_json_data(data)

    return return_bad_request()
