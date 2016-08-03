# -*- coding: utf-8 -*-
from pin.api6.http import return_json_data, return_un_auth, return_bad_request
from pin.api_tools import media_abs_url
from pin.tools import AuthCache
from pin.model_mongo import Notif
from pin.models_redis import NotificationRedis
from pin.api6.tools import get_simple_user_object,\
    get_next_url, post_item_json


def notif_count(request, startup=None):
    token = request.GET.get('token', '')
    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()
    notif_count = NotificationRedis(user_id=current_user).get_notif_count()
    if startup:
        return notif_count
    else:
        return return_json_data({'status': True, 'notif_count': notif_count})


def notif(request):
    """List of user notification."""
    data = {}
    token = request.GET.get('token', False)
    offset = int(request.GET.get('offset', 0))
    notifs_list = []
    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': 1000}

    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    NotificationRedis(user_id=current_user).clear_notif_count()
    if offset:
        notifs = NotificationRedis(user_id=current_user).get_notif(start=offset + 1)
    else:
        notifs = NotificationRedis(user_id=current_user).get_notif()

    for notif in notifs:
        data_extra = {}
        data_extra['id'] = str(notif.id)
        data_extra['actor'] = get_simple_user_object(notif.last_actor, current_user)
        data_extra['owner'] = get_simple_user_object(notif.owner)

        if isinstance(notif.date, int):
            data_extra['date'] = int(notif.date)
        else:
            data_extra['date'] = int(notif.date.strftime("%s"))

        if notif.type == Notif.LIKE:
            data_extra['text'] = "تصویر شمارا پسندید."
            try:
                post_object = post_item_json(notif.post, current_user, request)
            except:
                post_object = {}
            data_extra['post'] = post_object
            data_extra['type'] = Notif.LIKE

        elif notif.type == Notif.FOLLOW:
            data_extra['type'] = Notif.FOLLOW
            data_extra['text'] = "شما را دنبال می کند."

        elif notif.type == Notif.COMMENT:
            data_extra['type'] = Notif.COMMENT
            data_extra['text'] = "برای تصویر شما نظر داد"
            try:
                post_object = post_item_json(notif.post, current_user, request)
            except IndexError:
                post_object = {}
            data_extra['post'] = post_object

        elif Notif.DELETE_POST:
            if notif.post_image:
                data_extra['type'] = Notif.DELETE_POST
                data_extra['post_image'] = media_abs_url(notif.post_image)
        else:
            continue

        notifs_list.append(data_extra)

    data['objects'] = notifs_list

    if data['objects']:
        data['meta']['next'] = get_next_url(url_name='api-6-notif-notif',
                                            token=token, offset=offset + 20)
    return return_json_data(data)
