from pin.tools import AuthCache
from pin.api6.http import return_json_data, return_not_found, return_un_auth, return_bad_request
from pin.models import Post
from pin.api6.tools import get_int, get_user_data, get_next_url
from pin.tools import get_post_user_cache
from pin.models_redis import LikesRedis


def like_post(request, item_id):
    token = request.GET.get('token', False)
    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    try:
        post = get_post_user_cache(post_id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    from pin.models_redis import LikesRedis
    like, dislike, current_like = LikesRedis(post_id=item_id)\
        .like_or_dislike(user_id=current_user, post_owner=post.user_id)

    if like:
        user_act = 1
        user = get_user_data(current_user)
    elif dislike:
        user_act = -1
        user = {}

    data = {'likes': current_like, 'user_act': user_act, 'user': user}
    return return_json_data(data)


def post_likers(request, item_id):
    data = {}
    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': 1000}
    likers_list = []
    before = request.GET.get('before', False)
    if not before:
        before = 0

    try:
        post = get_post_user_cache(post_id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    if before:
        likers = LikesRedis(post_id=post.id).get_likes(offset=get_int(before), limit=12, as_user_object=True)
    else:
        likers = LikesRedis(post_id=post.id).get_likes(offset=0, limit=12, as_user_object=True)

    try:
        for user in likers:
            likers_list.append(get_user_data(user.id))
    except Exception as e:
        print e

    data['objects'] = likers_list
    if data['objects']:
        data['meta']['next'] = get_next_url(url_name='api-6-likers-post',
                                            before=int(before) + 20,
                                            url_args={"item_id": item_id})
    return return_json_data({'status': True, 'post_likers': data})