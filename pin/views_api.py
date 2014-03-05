import json
import datetime
from time import mktime
from django.http import HttpResponse

from models import Post


class MyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


def post(request):

    data = {}
    posts = Post.objects.all()
    objects_list = []

    for t in posts:
        o = {}
        for s in ['id', 'text', 'image', 'category_id', 'cnt_comment', 'cnt_like']:
            o[s] = getattr(t, s)

        objects_list.append(o)

    data['objects'] = objects_list
    json_data = json.dumps(data, cls=MyEncoder)

    return HttpResponse(json_data)
