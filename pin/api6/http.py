try:
    import simplejson as json
except ImportError:
    import json

from django.utils.translation import ugettext as _
from django.http import HttpResponse


def return_bad_request(message=_("Bad request")):
    data = '{"message":"%(message)s", "status":"400"}' % ({"message": message})
    return HttpResponse(data,
                        content_type="application/json",
                        status=400)


def return_not_found():
    return HttpResponse('{"message":"Not found", "status":"404"}',
                        content_type="application/json",
                        status=404)


def return_un_auth():
    return HttpResponse('{"message":"authentication faild", "status":"403"}',
                        content_type="application/json",
                        status=403)


def return_json_data(data):
    return HttpResponse(json.dumps(data), content_type='application/json')
