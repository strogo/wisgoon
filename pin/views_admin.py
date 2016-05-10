# -*- coding: utf-8 -*-
import json
import redis

from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden,\
    HttpResponse

from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils.translation import ugettext as _
from user_profile.models import Profile

from pin.models import Post, Comments, Log
from pin.tools import get_user_ip

User = get_user_model()
r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


def is_admin(user):
    if user.is_superuser:
        return True

    return False


def change_level(request, user_id, level):
    if not is_admin(request.user):
        return HttpResponseForbidden(_("You do not have permission to view this page"))

    Profile.objects.filter(user_id=user_id).update(level=level)

    return HttpResponseRedirect(reverse('pin-user', args=[user_id]))


def activate_user(request, user_id, status):
    if not is_admin(request.user):
        return HttpResponseForbidden(_("You do not have permission to view this page"))

    status = bool(int(status))
    user = User.objects.get(pk=user_id)
    user.is_active = status
    user.save()
    if not status:
        q = request.GET.get("q", "")
        Log.ban_by_admin(actor=request.user,
                         user_id=user_id,
                         text="%s || %s" % (user.username, q),
                         ip_address=get_user_ip(request))
    return HttpResponseRedirect(reverse('pin-user', args=[user_id]))


@login_required
def goto_index(request, item_id, status):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')

    status = int(status)
    if status == 1:
        Post.add_to_home(post_id=item_id)
    else:
        Post.remove_from_home(post_id=item_id)
    data = [{
        'status': status,
        'url': reverse('pin-item-goto-index', args=[item_id, int(not(status))])
    }]

    return HttpResponse(json.dumps(data))


@login_required
def comment_delete(request, id):
    comment = get_object_or_404(Comments, pk=id)
    post_id = comment.object_pk.id

    if not request.user.is_superuser:
        if comment.user.id != request.user.id:
            if comment.object_pk.user.id != request.user.id:
                return HttpResponseRedirect(reverse('pin-item', args=[post_id]))

    comment.delete()
    if request.is_ajax():
        data = {'status': True, 'message': _("Comment removed")}
        return HttpResponse(json.dumps(data), content_type="application/json")
    return HttpResponseRedirect(reverse('pin-item', args=[post_id]))
