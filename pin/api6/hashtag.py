# -*- coding: utf-8 -*-
from pin.tools import AuthCache
from pin.models import Post
from pin.api6.tools import get_next_url, get_int, get_objects_list
from pin.api6.http import return_json_data, return_bad_request
from haystack.query import SearchQuerySet


def hashtag(request):
    token = request.GET.get('token', '')
    query = str(request.GET.get('q', ''))
    query = query.replace('#', '')
    before = get_int(request.GET.get('before', 0))

    row_per_page = 20
    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    if query and token:

        results = SearchQuerySet().models(Post)\
            .filter(tags=query)\
            .order_by('-timestamp_i')[before:before + 1 * row_per_page]

        cur_user = AuthCache.id_from_token(token=token)
        posts = []
        for p in results:
            try:
                pp = Post.objects\
                    .only(*Post.NEED_KEYS2)\
                    .get(id=p.object.id)

                posts.append(pp)
            except:
                pass

        data['objects'] = get_objects_list(posts, cur_user_id=cur_user, r=request)

        if data['objects']:
            data['meta']['next'] = get_next_url(url_name='api-6-hashtag',
                                                before=20,
                                                token=token,
                                                q=query
                                                )
        return return_json_data(data)
    else:
        return return_bad_request()
