
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden

from user_profile.models import Profile


def is_admin(user):
    if user.is_superuser:
        return True

    return False


def activate_user(request, user_id, status):
    if not is_admin(request.user):
        return HttpResponseForbidden('cant access')

    status = bool(int(status))
    user = User.objects.get(pk=user_id)
    user.is_active = status
    user.save()
    return HttpResponseRedirect(reverse('pin-user', args=[user_id]))


def post_accept(request, user_id, status):
    if not is_admin(request.user):
        return HttpResponseForbidden('cant access')

    status = bool(int(status))
    Profile.objects.filter(user_id=user_id).update(post_accept_admin=status)

    return HttpResponseRedirect(reverse('pin-user', args=[user_id]))
