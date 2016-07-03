import emoji
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _

from pin.tools import AuthCache
from pin.models import Comments, Post
from pin.api6.tools import get_int, get_next_url,\
    get_comments, comment_objects_list, comment_item_json
from pin.api6.http import return_json_data, return_not_found, return_un_auth,\
    return_bad_request
from pin.tools import check_block, get_post_user_cache
from pin.toolkit import check_auth


def comment_post(request, item_id):
    limit = 20
    data = {}
    data['objects'] = {}
    data['meta'] = {'limit': limit, 'next': '', 'total_count': 1000}
    before = int(request.GET.get('before', 0))

    comments = get_comments(item_id, limit, before)
    data['objects'] = comment_objects_list(comments)

    data['meta']['next'] = get_next_url(url_name='api-6-comment-post',
                                        before=before + limit,
                                        url_args={"item_id": item_id}
                                        )
    return return_json_data(data)


@csrf_exempt
def add_comment(request, item_id):
    user = check_auth(request)
    if not user:
        return return_json_data({
            'status': False,
            'message': _('error in user validation')
        })

    try:
        post = get_post_user_cache(post_id=get_int(item_id))
        # post = Post.objects.get(id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    text = request.POST.get('comment', False)
    if not text:
        return return_json_data({
            'status': False,
            'message': _('Please Enter Your Comment')
        })

    if check_block(user_id=post.user_id, blocked_id=request.user.id):
        return return_json_data({
            'status': False,
            'message': _('This User Has Blocked You')
        })
    try:
        text = emoji.demojize(text)
        comment = Comments.objects.create(object_pk=post, comment=text,
                                          user_id=get_int(user.id),
                                          ip_address=user._ip)
        comment_data = comment_item_json(comment)
        comment_data['status'] = True
        comment_data['message'] = _('Successfully was Create Comment.')
        return return_json_data(comment_data)
    except:
        return return_json_data({
            'status': False,
            'message': _('Unsuccessfully was Create Comment.')
        })


def delete_comment(request, comment_id):
    token = request.GET.get('token', '')
    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    try:
        comment = Comments.objects.get(id=get_int(comment_id))
    except Comments.DoesNotExist:
        return return_not_found()

    if comment.user_id == current_user or comment.object_pk.user.id == current_user:
        comment_id = comment.id
        comment.delete()
        data = {'status': True,
                'message': _('Successfully Removed Comment'),
                'comment_id': comment_id}
    else:
        data = {'status': False,
                'message': _('Access Denied')}
    return return_json_data(data)


@csrf_exempt
def report(request, comment_id):
    token = request.GET.get('token', '')
    if token:
        current_user = AuthCache.id_from_token(token=token)
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
