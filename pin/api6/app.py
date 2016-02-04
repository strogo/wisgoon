# -*- coding: utf-8 -*-
"""Application api."""

from pin.api6.http import return_json_data
from pin.api_tools import media_abs_url
from pin.models import App_data


def latest(request):
    """Return latest version data."""
    app = App_data.objects.filter(current=True)[0]

    data = {
        "name": app.name,
        "file": media_abs_url(app.file.url),
        "version": app.version,
        "version_code": app.version_code,
    }

    return return_json_data(data)
