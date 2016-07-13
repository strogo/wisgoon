from pin.models import Campaign, Post
from pin.api6.tools import campaign_sample_json
from pin.api6.http import return_json_data, return_not_found
# from pin.tools import AuthCache
from pin.api6.tools import post_item_json, get_next_url
from haystack.query import SearchQuerySet
from pin.tools import AuthCache


def current_campaign(request, startup=None):
    data = {'meta': {'limit': 1,
                     'next': '',
                     'total_count': 0
                     },
            'objects': []
            }

    current = Campaign.objects.filter(is_current=True, expired=False).order_by('?').first()
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

    campaigns = Campaign.objects.filter(is_current=True, expired=False)\
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
    token = request.GET.get('token', False)
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

    posts = SearchQuerySet().models(Post).filter(tags__in=tags)\
        .order_by('-timestamp_i')[before:before + 20]

    for post in posts:
        post_json = post_item_json(post_id=post.pk, cur_user_id=user.id)
        if post_json:
            data['objects'].append(post_json)

    data['meta']['next'] = get_next_url(url_name='api-6-campaign-posts',
                                        before=before + 20,
                                        url_args={"camp_id": camp_id}
                                        )
    return return_json_data(data)
