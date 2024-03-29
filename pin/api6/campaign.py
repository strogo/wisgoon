# from django.core.cache import cache
from django.db.models import Q

from pin.models import Campaign
from pin.api6.tools import campaign_sample_json
from pin.api6.http import return_json_data, return_not_found
# from pin.tools import AuthCache
from pin.api6.tools import post_item_json, get_next_url
from pin.tools import AuthCache
from pin.models_es import ESPosts
# from haystack.query import SearchQuerySet
# from haystack.query import SQ
# from haystack.query import Raw


LIMIT = 10


def current_campaign(request, startup=None):
    data = {
        'meta': {
            'limit': 1,
            'next': '',
            'total_count': 0
        },
        'objects': []
    }

    current = Campaign.objects.filter(is_current=True, expired=False)\
        .order_by('?').first()
    if current:
        data['objects'].append(campaign_sample_json(current))

    if startup:
        return data
    else:
        return return_json_data(data)


def list(request):
    data = {'meta': {'limit': 1,
                     'next': '',
                     'total_count': 0
                     },
            'objects': []
            }

    before = int(request.GET.get('before', 0))

    campaigns = Campaign.objects\
        .filter(Q(is_current=True, expired=False) |
                Q(expired=True))\
        .order_by('-id')[before:before + 20]

    for campaign in campaigns:
        data['objects'].append(campaign_sample_json(campaign))
    return return_json_data(data)


def campaign_posts(request, camp_id):
    data = {'meta': {'limit': 1,
                     'next': '',
                     'total_count': 0
                     },
            'objects': []
            }
    # return return_json_data(data)

    token = request.GET.get('token', False)
    order_by_req = request.GET.get('order', False)
    if order_by_req == "timestamp_i":
        # order_by = "timestamp_i"
        order_by = "timestamp"
    else:
        # order_by_req = "timestamp_i"
        order_by_req = "cnt_like"
        order_by = "cnt_like"

    user = False
    if token:
        user = AuthCache.user_from_token(token=token)

    try:
        campaign = Campaign.objects.get(id=int(camp_id))
    except:
        return return_not_found()

    before = int(request.GET.get('before', 0))

    campaign_tags = campaign.tags
    tags = campaign_tags.split(',')
    tags.append(campaign.primary_tag)
    start_date = int(campaign.start_date.strftime("%s"))
    end_date = int(campaign.end_date.strftime("%s"))

    ps = ESPosts()
    if order_by == "timestamp":

        posts = ps.search_campaign(text=tags,
                                   offset=before,
                                   limit=LIMIT,
                                   order=order_by)

        # posts = SearchQuerySet().models(Post).filter(tags__in=tags)\
        #     .order_by('-{}'.format(order_by))[before:before + LIMIT]
    else:
        posts = ps.search_campaign(text=tags,
                                   range_date=[start_date, end_date],
                                   offset=before,
                                   limit=LIMIT,
                                   order=order_by)

    # posts = SearchQuerySet().models(Post).filter(tags__in=tags)\
    #     .filter(timestamp_i__gte=start_date,
    #             timestamp_i__lte=end_date)\
    #     .order_by('-{}'.format(order_by))[before:before + LIMIT]

    for post in posts:
        if user:
            post_json = post_item_json(post_id=post.id, cur_user_id=user.id)
        else:
            post_json = post_item_json(post_id=post.id)
        if post_json:
            data['objects'].append(post_json)

    data['meta']['next'] = get_next_url(url_name='api-6-campaign-posts',
                                        before=before + LIMIT,
                                        url_args={"camp_id": camp_id},
                                        order=order_by_req,
                                        )
    return return_json_data(data)


def search(request, camp):
    data = {}
    data['meta'] = {'limit': 20, 'next': ""}
    data['objects'] = []
    # return return_json_data(data)

    # words = camp.split()
    # sq = SQ()
    # for w in words:
    #     sq.add(SQ(text__contains=Raw("%s*" % w)), SQ.OR)
    #     sq.add(SQ(text__contains=Raw(w)), SQ.OR)

    # results = SearchQuerySet().models(Campaign).filter(sq)
    results = Campaign.objects.filter(tags__icontains=camp)
    for result in results:
        data['objects'].append(campaign_sample_json(result))
    return return_json_data(data)
