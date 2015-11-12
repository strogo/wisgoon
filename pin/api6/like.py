from pin.tools import AuthCache
from pin.api6.http import return_json_data, return_not_found, return_un_auth
from pin.models import Post
from pin.api6.tools import get_int, get_user_data
from pin.tools import get_post_user_cache


def like_post(request, item_id):
    token = request.GET.get('token', False)
    if token:
        current_user = AuthCache.id_from_token(token=token)
    else:
        return return_un_auth()

    try:
        post = get_post_user_cache(post_id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    from pin.models_redis import LikesRedis
    like, dislike, current_like = LikesRedis(post_id=item_id)\
        .like_or_dislike(user_id=current_user, post_owner=post.user_id)

    if like:
        user_act = 1
    elif dislike:
        user_act = -1

    data = {'likes': current_like, 'user_act': user_act}
    return return_json_data(data)


def post_likers(request, item_id):
    data = {}
    likers_list = []
    try:
        post = get_post_user_cache(post_id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    from pin.models_redis import LikesRedis
    post.likes = LikesRedis(post=post).get_likes(offset=0, limit=12, as_user_object=True)
    try:
        for user in post.likes:
            likers_list.append(get_user_data(user.id))
    except Exception as e:
        print e
    data['likers'] = likers_list
    return return_json_data({'status': True, 'post_likers': data})
