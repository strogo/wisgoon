from pin.tools import AuthCache
from pin.api6.http import return_json_data, return_un_auth, return_bad_request
from pin.model_mongo import NotifCount, Notif
from pin.api6.tools import get_list_post, get_objects_list, get_user_data, get_next_url


def notif_count(request):
    token = request.GET.get('token', '')
    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()
    try:
        notif_count = NotifCount.objects.filter(owner=current_user).first().unread
    except:
        notif_count = 0
    return return_json_data({'status': True, 'notif_count': notif_count})


def notif(request):

    data = {}
    token = request.GET.get('token', False)
    before = request.GET.get('before', False)
    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': 1000}
    if before:
        notifs = Notif.objects.filter(owner=current_user, id__lt=before).order_by('-date')[:20]
    else:
        notifs = Notif.objects.filter(owner=current_user).order_by('-date')[:20]
    notifs_list = []
    for notif in notifs:
        data_extra = {}
        if notif.type == Notif.LIKE:
            data_extra['actor'] = get_user_data(notif.last_actor)
            data_extra['owner'] = get_user_data(notif.owner)
            try:
                posts = get_list_post([notif.post])
                post_object = get_objects_list(posts, cur_user_id=current_user, r=request)[0]
            except IndexError:
                post_object = {}
            data_extra['post'] = post_object
            data_extra['type'] = Notif.LIKE
            data_extra['id'] = str(notif.id)
            notifs_list.append(data_extra)

        elif notif.type == Notif.FOLLOW:
            data_extra['actor'] = get_user_data(notif.last_actor)
            data_extra['owner'] = get_user_data(notif.owner)
            data_extra['type'] = Notif.FOLLOW
            data_extra['id'] = str(notif.id)
            notifs_list.append(data_extra)

        elif notif.type == Notif.COMMENT:
            data_extra['actor'] = get_user_data(notif.last_actor)
            data_extra['owner'] = get_user_data(notif.owner)
            data_extra['id'] = str(notif.id)
            data_extra['type'] = Notif.COMMENT
            try:
                posts = get_list_post([notif.post])
                post_object = get_objects_list(posts, cur_user_id=current_user, r=request)[0]
            except IndexError:
                post_object = {}
            data_extra['post'] = post_object
            notifs_list.append(data_extra)

        else:
            data_extra['actor'] = get_user_data(notif.last_actor)
            data_extra['owner'] = get_user_data(notif.owner)
            data_extra['type'] = Notif.DELETE_POST
            data_extra['id'] = str(notif.id)
            notifs_list.append(data_extra)

    data['objects'] = notifs_list

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-notif-notif',
                                            token=token, before=last_item)
    return return_json_data(data)
