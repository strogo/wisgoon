try:
    import simplejson as json
except ImportError:
    import json

from django.utils.translation import ugettext as _
from django.http import HttpResponse


def return_bad_request(message=_("Bad request"), status=False):
    data = {
        'status': status,
        'message': message,
    }
    return HttpResponse(json.dumps(data),
                        content_type="application/json",
                        status=400)


def return_not_found(status=False, message=_("Not found")):
    data = {
        'status': status,
        'message': message,
    }
    return HttpResponse(json.dumps(data),
                        content_type="application/json",
                        status=404)


def return_un_auth(message=_("authentication failed"), status=False):
    data = {
        'status': status,
        'message': message,
    }
    return HttpResponse(json.dumps(data),
                        content_type="application/json",
                        status=403)


def return_json_data(data):
    jdata = json.dumps(data)
    return HttpResponse(jdata, content_type='application/json')


def return_data(data):
    return HttpResponse(data, content_type='application/json')
