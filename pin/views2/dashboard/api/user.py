from haystack.query import SearchQuerySet
from user_profile.models import Profile
from pin.api6.tools import get_next_url, get_simple_user_object, get_profile_data
from pin.api6.http import return_json_data, return_un_auth
from pin.views2.dashboard.api.tools import check_admin


def search_user(request):
    if not check_admin(request):
        return return_un_auth()
    query = request.GET.get('q', '')
    before = int(request.GET.get('before', 0))
    token = request.GET.get('token', '')
    data = {}
    data['meta'] = {'limit': 20, 'next': ""}
    data['objects'] = []

    profiles = SearchQuerySet().models(Profile)\
        .filter(content__contains=query)[before:before + 20]

    for profile in profiles:
        profile = profile.object
        details = {}

        details['user'] = get_simple_user_object(profile.user.id)
        details['profile'] = get_profile_data(profile, profile.user.id)
        data['objects'].append(details)

        if data['objects']:
            data['meta']['next'] = get_next_url(url_name='api-6-post-search',
                                                token=token,
                                                before=before + 20)
    return return_json_data(data)
