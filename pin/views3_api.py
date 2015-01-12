import json

from django.conf import settings
from django.http import HttpResponse


from pin.models import Post

from pin.api_tools import get_r_data, get_list_post, get_objects_list,\
    MyEncoder, get_next_url


def post_latest(request):

    before, cuser, tsize, before, token = get_r_data(request)

    data = {}
    data['meta'] = {'limit': 10,
                    'next': '',
                    'offset': 0,
                    'previous': '',
                    'total_count': 1000}

    pl = Post.latest(pid=before)
    posts = get_list_post(pl, from_model=settings.STREAM_LATEST)

    data['objects'] = get_objects_list(posts,
                                       cur_user_id=cuser,
                                       thumb_size=tsize,
                                       r=request)

    if pl:
        data['meta']['next'] = get_next_url(url_name='api-3-latest', before=pl[-1:][0], token=token)
    json_data = json.dumps(data, cls=MyEncoder)
    return HttpResponse(json_data)
