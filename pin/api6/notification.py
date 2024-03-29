# -*- coding: utf-8 -*-
from pin.api6.http import return_json_data, return_un_auth, return_bad_request
from pin.api_tools import media_abs_url
from pin.model_mongo import Notif
from pin.models import FollowRequest
from pin.models_redis import NotificationRedis
from pin.tools import AuthCache
from pin.api6.tools import get_simple_user_object, get_next_url, post_item_json

# from django.conf import settings
# import requests
# import json


def notif_count(request, startup=None):
    token = request.GET.get('token', '')
    cnt_request = 0
    total_count = 0
    if token:
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            if startup:
                return total_count
            return return_un_auth()
    else:
        if startup:
            return total_count
        return return_bad_request()

    notif_count = NotificationRedis(user_id=current_user.id).get_notif_count()

    if current_user.profile.is_private:
        cnt_request = FollowRequest.objects\
            .filter(target=current_user).count()

    total_count = str(int(notif_count) + cnt_request)

    if startup:
        return total_count
    else:
        return return_json_data({'status': True, 'notif_count': total_count})


def notif(request):
    # data = {}
    # data['objects'] = []
    # data['meta'] = {'limit': 20, 'next': '', 'total_count': 1000}
    # payload = {}
    # offset = int(request.GET.get('offset', 0))
    # token = request.GET.get('token', None)

    # if token:
    #     payload['token'] = token
    # if offset:
    #     payload['before'] = offset

    # if settings.DEBUG:
    #     url = "http://127.0.0.1:8801/v7/notif/"
    # else:
    #     url = "http://api.wisgoon.com/v7/notif/"

    # # Get choices post
    # s = requests.Session()
    # res = s.get(url, params=payload, headers={'Connection': 'close'})

    # if res.status_code == 200:
    #     try:
    #         data = json.loads(res.content)
    #     except:
    #         pass
    """List of user notification."""
    user_obj = {}
    token = request.GET.get('token', False)
    offset = int(request.GET.get('offset', 0))
    data = {
        'meta': {'next': '',
                 'limit': 20,
                 'total_count': 1000},
        'objects': [],
        'follow_requests': {}
    }

    notifs_list = []

    if token:
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    NotificationRedis(user_id=current_user.id).clear_notif_count()
    if offset:
        notifs = NotificationRedis(user_id=current_user.id)\
            .get_notif(start=offset)
    else:
        notifs = NotificationRedis(user_id=current_user.id).get_notif()

        """ check profile is private """
        if current_user.profile.is_private:

            """ Get follow request """
            follow_requests = FollowRequest.objects\
                .filter(target_id=current_user.id).order_by('-id')

            cnt_requests = follow_requests.count()
            if cnt_requests > 0:
                last_follow_req = follow_requests[0]
                user_obj = get_simple_user_object(last_follow_req.user.id)

                data['follow_requests'] = {'user': user_obj,
                                           'cnt_requests': cnt_requests}

    last_date = None
    for notif in notifs:
        if notif.date:
            last_date = notif.date

        data_extra = {}
        data_extra['id'] = str(notif.id)
        data_extra['actor'] = get_simple_user_object(notif.last_actor,
                                                     current_user.id)
        data_extra['owner'] = get_simple_user_object(notif.owner)

        if isinstance(notif.date, int):
            data_extra['date'] = int(notif.date)
        else:
            data_extra['date'] = int(notif.date.strftime("%s"))

        if notif.type == Notif.LIKE:
            data_extra['text'] = "تصویر شمارا پسندید"
            try:
                post_object = post_item_json(notif.post,
                                             current_user.id,
                                             request)
            except:
                post_object = {}

            if not post_object:
                continue

            data_extra['post'] = post_object
            data_extra['type'] = Notif.LIKE

        elif notif.type == Notif.FOLLOW:
            data_extra['type'] = Notif.FOLLOW
            data_extra['text'] = "شما را دنبال می کند"

        elif notif.type == Notif.ACCEPT_FOLLOW_REQUEST:
            data_extra['type'] = Notif.ACCEPT_FOLLOW_REQUEST
            data_extra['text'] = "درخواست شما را پذیرفت"

        elif notif.type == Notif.FOLLOW_REQUEST:
            data_extra['type'] = Notif.FOLLOW_REQUEST
            data_extra['text'] = "میخواهد شما را دنبال کند"

        elif notif.type == Notif.COMMENT:
            data_extra['type'] = Notif.COMMENT
            data_extra['text'] = "مطلبی را با شما به اشتراک گذاشته"
            try:
                post_object = post_item_json(notif.post,
                                             current_user.id,
                                             request)
            except IndexError:
                post_object = {}

            if not post_object:
                continue

            data_extra['post'] = post_object

        elif notif.type == Notif.DELETE_POST:
            if notif.post_image:
                data_extra['type'] = Notif.DELETE_POST
                data_extra['post_image'] = media_abs_url(notif.post_image)
        else:
            continue

        notifs_list.append(data_extra)

    data['objects'] = notifs_list

    if data['objects']:
        data['meta']['next'] = get_next_url(url_name='api-6-notif-notif',
                                            token=token, offset=last_date)
    return return_json_data(data)
