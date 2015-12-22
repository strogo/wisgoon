from pin.tools import AuthCache
from pin.api6.http import return_json_data, return_not_found, return_un_auth,\
    return_bad_request
from pin.models import Comments, Post
from django.views.decorators.csrf import csrf_exempt
from pin.api6.tools import get_int, get_next_url,\
    get_comments, comment_objects_list, comment_item_json
from django.utils.translation import ugettext as _


def comment_post(request, item_id):
    limit = 20
    data = {}
    data['objects'] = {}
    data['meta'] = {'limit': limit, 'next': '', 'total_count': 1000}
    before = request.GET.get('before', 0)

    comments = get_comments(item_id, limit, before)
    data['objects'] = comment_objects_list(comments)

    if len(data['objects']) == 20:
        last_item = (before + 1) * limit
        data['meta']['next'] = get_next_url(url_name='api-6-comment-post',
                                            before=last_item,
                                            url_args={"item_id": item_id}
                                            )
    return return_json_data(data)


@csrf_exempt
def add_comment(request, item_id):
    token = request.GET.get('token', '')
    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    try:
        post = Post.objects.get(id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    text = request.POST.get('comment', False)
    if not text:
        return return_json_data({'status': False, 'message': _('Please Enter Your Comment')})

    try:
        comment = Comments.objects.create(object_pk=post, comment=text,
                                          user_id=get_int(current_user))
        comment_data = comment_item_json(comment)
        comment_data['message'] = 'Successfully Create Comment.'
        return return_json_data(comment_data)
    except:
        return return_json_data({'status': False, 'message': _('Unsuccessfully Create Comment.')})


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
                'message': _('Successfully Delete Comment'),
                'comment_id': comment_id}
    else:
        data = {'status': False,
                'message': _('Access Denied Comment')}
    return return_json_data(data)
