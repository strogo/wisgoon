# -*- coding: utf-8 -*-
"""Application api."""

from pin.api6.http import return_json_data
from pin.api_tools import media_abs_url
from pin.models import App_data
from pin.api6.tools import system_read_only


def latest(request, startup=None):
    """Return latest version data."""
    app = App_data.objects.filter(current=True)[0]

    data = {
        "name": app.name,
        "file": media_abs_url(app.file.url),
        "version": app.version,
        "version_code": app.version_code,
    }
    if startup:
        return data
    else:
        return return_json_data(data)


def startup_data(request):
    from pin.api6.notification import notif_count
    from pin.api6.campaign import current_campaign
    from pin.api6.app import latest
    from pin.api6.auth import get_phone_data
    import requests

    token = request.GET.get('token', False)
    data = {}
    ads = {
        "advertisement": {
            "adad": False,
            "agahist": True
        }
    }

    get_phone_data(request, startup=None)

    try:
        response = requests.get('http://agahist.com/mobileAdStatus/wisgoonv6/', timeout=0.15)
        if response.status_code == 200:
            ads = response.json()
    except requests.exceptions.Timeout:
        pass
    except requests.exceptions.ConnectionError:
        pass

    data['campaign'] = current_campaign(request, startup=True)

    if token:
        data['notif_count'] = notif_count(request, startup=True)
    else:
        data['notif_count'] = 0

    data['app_version'] = latest(request, startup=True)
    data['ads'] = ads
    data['read_only'] = system_read_only()
    return return_json_data(data)
