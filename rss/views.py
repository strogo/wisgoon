# -*- coding: utf8 -*- 

from django.shortcuts import render_to_response, get_object_or_404
from rss.models import Item, Feed, Subscribe, Likes
from django.template.context import RequestContext
from rss.forms import FeedForm
from django.http import HttpResponseRedirect  #, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.urlresolvers import reverse
import json

def home(request):
    
    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    
    if timestamp == 0:
        latest_items = Item.objects.select_related().all().order_by('-timestamp')[:30]
    else:
        latest_items = Item.objects.select_related().all().extra(where=['timestamp<%s'], params=[timestamp]).order_by('-timestamp')[:30]
    
    try:   
        user_feeds = Subscribe.objects.filter(user=request.user).all()
    except :
        user_feeds = ""
        
        
    if request.is_ajax():
        return render_to_response('rss/_items.html', 
                              {'latest_items': latest_items},
                              context_instance=RequestContext(request))
    else:
        return render_to_response('rss/home.html', 
                              {'latest_items': latest_items,'user_feeds':user_feeds},
                              context_instance=RequestContext(request))
        
def feed(request, feed_id):
    
    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    
    if timestamp == 0:
        feed = Feed.objects.get(pk=feed_id)
        latest_items = Item.objects.select_related().filter(feed=feed_id).all().order_by('-timestamp')[:30]
    else:
        latest_items = Item.objects.select_related().filter(feed=feed_id).all().extra(where=['timestamp<%s'], params=[timestamp]).order_by('-timestamp')[:30]
            
    if request.is_ajax():
        return render_to_response('rss/_items.html', 
                              {'latest_items': latest_items},
                              context_instance=RequestContext(request))
    else:
        return render_to_response('rss/feed.html', 
                              {'latest_items': latest_items, 'feed':feed},
                              context_instance=RequestContext(request))

def feed_item(request, feed_id, item_id):
    feed = Feed.objects.get(pk=feed_id)
    item = get_object_or_404(Item.objects.filter(feed=feed_id,id=item_id)[:1])
    
    return render_to_response('rss/item.html', 
                              {'item': item, 'feed':feed},
                              context_instance=RequestContext(request))

def feed_item_goto(request, item_id):
    item = get_object_or_404(Item.objects.filter(id=item_id)[:1])
    
    Item.objects.filter(id=item_id).update(goto=item.goto+1)
    
    return HttpResponseRedirect(item.url)
    
@login_required       
def subscribe(request):
    
    if request.method=="POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            feed, created = Feed.objects.get_or_create(url=url,defaults={'creator': request.user})
            
            sub, sub_created = Subscribe.objects.get_or_create(user=request.user,feed=feed)
            
            if sub_created:
                feed.followers = feed.followers+1
                feed.save()
                
            return HttpResponseRedirect('/')
    
    form = FeedForm()
    
    return render_to_response('rss/subscribe.html',{'form':form},context_instance=RequestContext(request))

@login_required
def like(request, item_id):

    try:
        item = Item.objects.get(pk=item_id)
        current_like = item.likes
        
        liked = Likes.objects.filter(user=request.user, item=item).count()
        
        user_act = 0
        
        if not liked:
            like = Likes()
            like.user = request.user
            like.item = item
            like.save()
            
            current_like = current_like+1
            user_act = 1
            
        else:
            current_like = current_like-1
            Likes.objects.filter(user=request.user,item=item).delete()
            user_act = -1
        
        Item.objects.filter(id=item_id).update(likes=current_like)
        
        if request.is_ajax():
            
            data = [{'likes': current_like, 'user_act':user_act}]
                       
            return HttpResponse(json.dumps(data))
        else:
            return HttpResponseRedirect(reverse('rss-item', args=[item.feed.id, item.id]))
            
    except Item.DoesNotExist:
        return HttpResponseRedirect('/')
        




