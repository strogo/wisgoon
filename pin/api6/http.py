try:
    import simplejson as json
except ImportError:
    import json

from django.utils.translation import ugettext as _
from django.http import HttpResponse


def return_bad_request(message=_("Bad request")):
    data = {
        'status': 400,
        'message': message,
    }
    return HttpResponse(json.dumps(data),
                        content_type="application/json",
                        status=400)


def return_not_found(message=_("Not found")):
    data = {
        'status': 404,
        'message': message,
    }
    return HttpResponse(json.dumps(data),
                        content_type="application/json",
                        status=404)


def return_un_auth(message=_("authentication failed")):
    data = {
        'status': 403,
        'message': message,
    }
    return HttpResponse(json.dumps(data),
                        content_type="application/json",
                        status=403)


def return_json_data(data):
    jdata = json.dumps(data)
    return HttpResponse(jdata, content_type='application/json')
