from pin.tools import AuthCache
from pin.api6.http import return_json_data, return_not_found, return_un_auth
from pin.models import Comments, Post
from django.views.decorators.csrf import csrf_exempt
from pin.api6.tools import get_int, get_json, get_next_url


def comment_post(request, item_id):
    data = {}
    comments_list = []
    data['objects'] = {}
    data['meta'] = {'limit': 20, 'next': '', 'total_count': 1000}
    before = request.GET.get('before', False)
    token = request.GET.get('token', '')
    # if token:
    #     current_user = AuthCache.id_from_token(token=token)
    if before:
        comments = Comments.objects.filter(id__lt=get_int(before)).order_by('-id')[:20]
    else:
        comments = Comments.objects.filter(object_pk_id=get_int(item_id)).order_by('-id')[:20]

    for comment in comments:
        comment_dict = {}
        comment_dict['id'] = comment.id
        comment_dict['comment'] = comment.comment
        comments_list.append(comment_dict)

    data['objects'] = comments_list

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-comment-post',
                                            token=token, before=last_item,
                                            url_args={"item_id": item_id}
                                            )

    return return_json_data(data)


@csrf_exempt
def add_comment(request, item_id):
    token = request.GET.get('token', '')
    if token:
        current_user = AuthCache.id_from_token(token=token)
    else:
        return return_un_auth()

    try:
        post = Post.objects.get(id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    comment_form = get_json(request.body)
    if not comment_form['comment']:
        data = {'status': False, 'message': 'Please Enter Your Comment'}
        return return_json_data(data)

    try:
        Comments.objects.create(object_pk=post,
                                comment=comment_form['comment'],
                                user_id=current_user)
        return return_json_data({'status': True, 'message': 'Successfully Create Comment.'})
    except:
        return return_json_data({'status': False, 'message': 'Unsuccessfully Create Comment.'})


def delete_comment(request, comment_id):
    token = request.GET.get('token', '')
    if token:
        current_user = AuthCache.id_from_token(token=token)
    else:
        return return_un_auth()

    converted_comment_id = get_int(comment_id)
    try:
        comment = Comments.objects.get(id=converted_comment_id)
    except Comments.DoesNotExist:
        return return_not_found()

    if comment.user_id == current_user or comment.object_pk.user.id == current_user:
        comment.delete()
        data = {'status': True, 'message': 'Successfully Delete Comment'}
    else:
        data = {'status': False, 'message': 'Access Denied Comment'}
    return return_json_data(data)
