# -*- coding: utf-8 -*-
"""Application api."""

from pin.api6.http import return_json_data
from pin.api_tools import media_abs_url
from pin.models import App_data
from pin.api6.tools import is_system_writable
from pin.tools import AuthCache
from user_profile.models import Package, Subscription
from datetime import datetime


def latest(request, startup=None):
    """Return latest version data."""
    app = App_data.objects.filter(current=True).first()
    if not app:
        return {}

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
    # from pin.api6.auth import get_phone_data
    # import requests

    token = request.GET.get('token', False)
    data = {}
    ads = {
        "advertisement": {
            "adad": False,
            "agahist": True
        }
    }

    # get_phone_data(request, startup=None)

    # try:
    #     url = "http://agahist.com/mobileAdStatus/wisgoonv6/"
    #     response = requests.get(url, timeout=0.15)
    #     if response.status_code == 200:
    #         ads = response.json()
    # except requests.exceptions.Timeout:
    #     pass
    # except requests.exceptions.ConnectionError:
    #     pass

    data['campaign'] = current_campaign(request, startup=True)
    data['packages'] = Package.all_packages()
    data['show_ads'] = True
    data['show_native_ads'] = True
    data['credit'] = 0

    if token:
        data['notif_count'] = notif_count(request, startup=True)

        current_user = AuthCache.user_from_token(token=token)
        if current_user:
            data['credit'] = current_user.profile.credit
            now = datetime.utcnow().strftime("%s")

            # Check subscription end_date
            subscription = Subscription.objects\
                .filter(user=current_user).order_by('-id').first()

            if subscription:
                end_date = (subscription[0].end_date).replace(tzinfo=None)\
                    .strftime("%s")

                if now >= end_date:
                    subscription.expire = True
                    subscription.save()
                else:
                    data['show_ads'] = False
                    data['show_native_ads'] = False

    else:
        data['notif_count'] = 0

    data['app_version'] = latest(request, startup=True)
    data['ads'] = ads
    data['read_only'] = is_system_writable()
    return return_json_data(data)
