from tastypie.models import ApiKey
from django.conf import settings
from pin.tools import AuthCache, get_user_ip


def check_auth(request):
    """User object has user_id and is_active."""
    token = request.GET.get('token', '')
    if not token:
        return False

    try:
        user = AuthCache.user_from_token(token)
        if not user:
            return False
        user._ip = get_user_ip(request)

        if not user.is_active:
            return False
        else:
            return user
    except ApiKey.DoesNotExist:
        return False

    return False


def get_read_only_system():
    return getattr(settings, 'READ_ONLY', False)
