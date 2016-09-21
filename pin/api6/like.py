from django.views.decorators.csrf import csrf_exempt
from django.http import UnreadablePostError
from django.utils.translation import ugettext as _

from pin.models import Post
from pin.models_redis import LikesRedis
from pin.tools import AuthCache, get_post_user_cache
from pin.api6.http import return_json_data, return_not_found, return_un_auth,\
    return_bad_request
from pin.api6.tools import get_int, get_simple_user_object, get_next_url,\
    is_system_writable


def like_post(request, item_id):
    if is_system_writable() is False:
        data = {
            'status': False,
            'message': _('Website update in progress.')
        }
        return return_json_data(data)

    token = request.GET.get('token', False)
    if token:
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    try:
        post = get_post_user_cache(post_id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    like, dislike, current_like = LikesRedis(post_id=item_id)\
        .like_or_dislike(user_id=current_user.id,
                         post_owner=post.user_id,
                         category=post.category_id)

    if like:
        user_act = 1
        user = get_simple_user_object(current_user.id, post.user_id)
    elif dislike:
        user_act = -1
        user = {}

    data = {'cnt_like': current_like, 'user_act': user_act, 'user': user}
    return return_json_data(data)


@csrf_exempt
def like_item(request):
    if is_system_writable() is False:
        data = {
            'status': False,
            'message': _('Website update in progress.')
        }
        return return_json_data(data)

    try:
        token = request.POST.get('token', False)
        item_id = int(request.POST.get('item_id', 0))
    except UnreadablePostError:
        return return_bad_request()

    if token:
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    try:
        post = get_post_user_cache(post_id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    like, dislike, current_like = LikesRedis(post_id=item_id)\
        .like_or_dislike(user_id=current_user.id,
                         post_owner=post.user_id,
                         category=post.category_id)

    if like:
        user_act = 1
        user = get_simple_user_object(current_user.id, post.user_id)
    elif dislike:
        user_act = -1
        user = {}

    data = {'cnt_like': current_like, 'user_act': user_act, 'user': user}
    return return_json_data(data)


def post_likers(request, item_id):
    data = {}
    current_user_id = None
    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': LikesRedis(post_id=item_id).cntlike()}
    likers_list = []
    before = request.GET.get('before', False)

    token = request.GET.get('token', False)
    if token:
        current_user = AuthCache.user_from_token(token=token)
        if current_user:
            current_user_id = current_user.id

    if not before:
        before = 0

    try:
        post = get_post_user_cache(post_id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    if before:
        likers = LikesRedis(post_id=post.id)\
            .get_likes(offset=get_int(before), limit=20, as_user_object=False)
    else:
        likers = LikesRedis(post_id=post.id)\
            .get_likes(offset=0, limit=20, as_user_object=False)

    for user in likers:
        try:
            u = {
                'user': get_simple_user_object(int(user), current_user_id)
            }
            likers_list.append(u)
        except Exception as e:
            print e

    data['objects'] = likers_list
    if data['objects']:
        data['meta']['next'] = get_next_url(url_name='api-6-likers-post',
                                            token=token,
                                            before=int(before) + 20,
                                            url_args={"item_id": item_id})
    return return_json_data(data)
