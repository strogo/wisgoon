from pin.models import SystemState
from django.core.cache import cache
from django.http import HttpResponse
import json
from django.utils.translation import ugettext as _


def system_writable(function):
    def wrap(request, *args, **kwargs):

        state = cache.get(SystemState.CACHE_NAME)
        if state is None:
            try:
                sys_state = SystemState.objects.get(id=1)
                state = sys_state.writable
            except SystemState.DoesNotExist:
                sys_state = SystemState.objects.create(writable=True)
                state = sys_state.writable

        if state:
            return function(request, *args, **kwargs)
        else:
            msg = _("Website update in progress.")
            data = {'status': False, 'message': msg, 'type': 'None'}
            return HttpResponse(json.dumps(data),
                                content_type='application/json')
            # if request.is_ajax():
            # else:
            #     messages.error(request, msg)
            #     return HttpResponseRedirect(request.path)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
