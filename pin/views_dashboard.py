import redis 
    
from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseBadRequest, Http404
from django.shortcuts import render

from models import Post

r_server = redis.Redis(settings.REDIS_DB, db=11)

def is_admin(user):
    if user.is_superuser:
        return True

    return False

def home(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('cant access')
    post_pending = Post.objects.filter(status=0).count()
    return render(request, 'dashboard/home.html', {"post_pending": post_pending})

def photos(request):
    if not is_admin(request.user):
        return HttpResponseForbidden('cant access')
    pendings = r_server.smembers('pending_photos')
    if not pendings:
        plist = Post.objects.filter(status=0).values_list('id', flat=True)[:100]
        for idp in plist:
            r_server.sadd('pending_photos', int(idp))
        
        pendings = r_server.smembers('pending_photos')
    
    idis = list(pendings)[:20]
    posts = Post.objects.filter(id__in=idis, status=0)
    return render(request, 'dashboard/photos.html', {'posts': posts})

def photos_accept(request, post_id):
    if not is_admin(request.user):
        return HttpResponseForbidden('cant access')
    post = Post.objects.get(id=post_id)
    post.approve()

    if request.is_ajax():
        return HttpResponse('1')
    return HttpResponseRedirect(reverse('dashboard-photos'))


def home_base(request):
    return render(request, 'dashboard/home.html')