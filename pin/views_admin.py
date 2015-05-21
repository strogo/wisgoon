# -*- coding: utf-8 -*-
import json
import redis

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.cache import cache
from django.http import HttpResponseRedirect, HttpResponseForbidden,\
    HttpResponse

from django.shortcuts import get_object_or_404, render
from django.conf import settings
from user_profile.models import Profile

from pin.models import Post, Comments, Log
from pin.context_processors import is_police
from model_mongo import Ads, FixedAds, UserMeta, PendingPosts

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


def is_admin(user):
    if user.is_superuser:
        return True

    return False


def ads_admin(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('cant access')

    ads = Ads.objects.only('user', 'post', 'cnt_view', 'ads_type', 'ended', 'start', 'end').order_by('-id')

    return render(request, 'pin2/ads_admin.html', {
        'ads': ads
    })


def pending_post(request, post, status=1):
    if is_police(request, flat=True):
        post_obj = Post.objects.get(id=post)
        if status == 1:
            if not PendingPosts.objects(post=post).count():
                PendingPosts.objects.create(user=request.user.id, post=post)
                Log.post_pending(post=post_obj, actor=request.user)
        else:
            PendingPosts.objects(user=request.user.id, post=post).delete()

    return HttpResponseRedirect(reverse('pin-item', args=[int(post)]))


def change_level(request, user_id, level):
    if not is_admin(request.user):
        return HttpResponseForbidden('cant access')

    UserMeta.objects(user=user_id).update(set__level=level, upsert=True)

    return HttpResponseRedirect(reverse('pin-user', args=[user_id]))


def ads_fixed_admin(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('cant access')

    delete = request.GET.get('delete', None)
    if delete:
        a = FixedAds.objects.get(id=delete)
        cache.delete("fixed_post")
        cache.delete("fixed_post_%d" % int(a.post))
        a.delete()
        return HttpResponseRedirect(reverse('ads-fixed-admin'))

    if request.method == "POST":
        post = int(request.POST.get('post'))
        ttl = int(request.POST.get('ttl'))
        if ttl and post:
            n_ttl = (ttl + 1) * 86400
            c_name = "fixed_post"
            c_name_p = "fixed_post_%d" % post
            FixedAds.objects.create(post=post, ttl=n_ttl)
            cache.set(c_name, post, n_ttl)
            cache.set(c_name_p, 0, n_ttl)

        return HttpResponseRedirect(reverse('ads-fixed-admin'))

    ads = FixedAds.objects.all()

    return render(request, 'pin2/ads_fixed_admin.html', {
        'ads': ads,
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
        if comment.user.id != request.user.id:
            if comment.object_pk.user.id != request.user.id:
                return HttpResponseRedirect(reverse('pin-item', args=[post_id]))

    comment.delete()
    if request.is_ajax():
        data = {'status': True, 'message': 'دیدگاه حذف شد'}
        return HttpResponse(json.dumps(data))

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
