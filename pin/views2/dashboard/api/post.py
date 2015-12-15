from pin.api6.http import return_json_data, return_not_found, return_un_auth
from pin.api6.tools import post_item_json
from pin.views2.dashboard.api.tools import post_reporter_user, get_reported_posts,\
    check_admin
from pin.models import Ad
from django.db.models import Count


def reported(request):
    if not check_admin(request):
        return return_un_auth()

    post_reporter_list = []
    reported_posts = get_reported_posts()

    if not reported_posts:
        return return_not_found()

    for post in reported_posts:
        post_item = post_item_json(post)
        post_item['reporter'] = post_reporter_user(post.id)
        post_reporter_list.append(post_item)

    return return_json_data(post_reporter_list)


def enable_ads(request):
    if not check_admin(request):
        return return_un_auth()
    point_list = []
    ads = Ad.objects.values('start').annotate(cnt_ad=Count('start'))\
        .filter(ended=False).order_by('-id')
    data = {}
    for ad in ads:
        timestamp = int(ad['start'].strftime('%s')) * 1000
        point_list.append([timestamp, ad['cnt_ad']])
    data['data'] = point_list
    data['name'] = 'Advertising'
    return return_json_data(data)


def disable_ads(request):
    if not check_admin(request):
        return return_un_auth()
    point_list = []
    ads = Ad.objects.values('start').annotate(cnt_ad=Count('start'))\
        .filter(ended=True).order_by('-id')
    data = {}
    for ad in ads:
        timestamp = int(ad['start'].strftime('%s')) * 1000
        point_list.append([timestamp, ad['cnt_ad']])
    data['data'] = point_list
    data['name'] = 'Advertising'
    return return_json_data(data)
