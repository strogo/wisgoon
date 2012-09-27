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
from rss.sphinxapi import SPH_MATCH_ALL, SphinxClient, SPH_ATTR_TIMESTAMP,\
    SPH_MATCH_EXTENDED, SPH_SORT_TIME_SEGMENTS
import sys

import time

def home(request):
    
    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    
    if timestamp == 0:
        latest_items = Item.objects.all().order_by('-timestamp')[:30]
    else:
        latest_items = Item.objects.all().extra(where=['timestamp<%s'], params=[timestamp]).order_by('-timestamp')[:30]
    
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
    
    feed = Feed.objects.get(pk=feed_id)
    
    if timestamp == 0:
        latest_items = Item.objects.filter(feed=feed_id).all().order_by('-timestamp')[:30]
    else:
        latest_items = Item.objects.filter(feed=feed_id).all().extra(where=['timestamp<%s'], params=[timestamp]).order_by('-timestamp')[:30]
            
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
    
    docs=search_query(item.title)
        
    result = Item.objects.filter(id__in=docs).all()
    
    return render_to_response('rss/item.html', 
                              {'item': item, 'feed':feed, 'latest_items':result},
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
def a_sub(request, feed_id):
    feed = get_object_or_404(Feed.objects.filter(id=feed_id)[:1])
    
    sub, sub_created = Subscribe.objects.get_or_create(user=request.user,feed=feed)
    if not sub_created:
        sub.delete()
    
    if request.is_ajax():
        data = [{'status':sub_created}]
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseRedirect(reverse('rss-feed', args=[feed_id]))
    
        

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

def search_query(query):
    
    mode = SPH_MATCH_EXTENDED
    host = 'localhost'
    port = 9312
    index = 'rss_item'
    filtercol = 'group_id'
    filtervals = []
    sortby = '-@weights'
    groupby = 'id'
    groupsort = '@group desc'
    limit = 30
    
    # do query
    cl = SphinxClient()
    cl.SetServer ( host, port )
    cl.SetWeights ( [100, 1] )
    cl.SetMatchMode ( mode )
    #cl.SetSortMode(SPH_SORT_TIME_SEGMENTS)
    if limit:
        cl.SetLimits ( 0, limit, max(limit,1000) )
    res = cl.Query ( query, index )
    
    docs =[]
    for item in res['matches']:
        docs.append(item['id'])
    
    return docs


def search(request):
    q = request.GET.get('q', '')
    docs=search_query(q)
        
    result = Item.objects.filter(id__in=docs).all()
    
    return render_to_response('rss/search.html',{'latest_items':result},context_instance=RequestContext(request))



