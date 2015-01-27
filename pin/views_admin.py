import json
import redis

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponseForbidden,\
    HttpResponse

from django.shortcuts import get_object_or_404, render
from django.conf import settings
from user_profile.models import Profile

from pin.models import Post, Comments
from model_mongo import Ads

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


def is_admin(user):
    if user.is_superuser:
        return True

    return False

def ads_admin(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('cant access')

    ads = Ads.objects.order_by('-id')

    return render(request, 'pin2/ads_admin.html', {
        'ads': ads
    })


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


@login_required
def item_fault(request, item_id):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')

    p = Post.objects.get(id=item_id)
    p.status = Post.FAULT
    p.report = 0
    p.save()

    user = p.user
    user.profile.fault = user.profile.fault + 1
    user.profile.save()
    return HttpResponse('1')


@login_required
def goto_index(request, item_id, status):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')

    if int(status) == 1:
        Post.objects.filter(pk=item_id).update(show_in_default=True)
        r_server.lpush(settings.HOME_STREAM, item_id)
        data = [{'status': 1,
                 'url': reverse('pin-item-goto-index', args=[item_id, 0])}]

        return HttpResponse(json.dumps(data))
    else:
        r_server.lrem(settings.HOME_STREAM, item_id)
        Post.objects.filter(pk=item_id).update(show_in_default=False)
        data = [{'status': 0,
                 'url': reverse('pin-item-goto-index', args=[item_id, 1])}]

        return HttpResponse(json.dumps(data))


@login_required
def comment_delete(request, id):
    comment = get_object_or_404(Comments, pk=id)
    post_id = comment.object_pk.id

    if not request.user.is_superuser:
        if comment.user != request.user:
            return HttpResponseRedirect(reverse('pin-item', args=[post_id]))

    comment.delete()

    return HttpResponseRedirect(reverse('pin-item', args=[post_id]))


@login_required
def comment_approve(request, id):
    if not request.user.is_superuser:
        return HttpResponse('error in authentication')

    comment = get_object_or_404(Comments, pk=id)
    comment.is_public = True
    comment.save()

    return HttpResponseRedirect(reverse('pin-item', args=[comment.object_pk.id]))


@login_required
def comment_unapprove(request, id):
    if not request.user.is_superuser:
        return HttpResponse('error in authentication')

    comment = get_object_or_404(Comments, pk=id)
    comment.is_public = False
    comment.save()

    return HttpResponseRedirect(reverse('pin-item', args=[comment.object_pk.id]))
