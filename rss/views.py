# -*- coding: utf8 -*- 

from django.shortcuts import render_to_response, get_object_or_404
from rss.models import Item, Feed, Subscribe, Likes ,Report, Search, Lastview
from django.template.context import RequestContext
from rss.forms import FeedForm ,ReportForm 
from django.http import HttpResponseRedirect  #, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.core.urlresolvers import reverse
import json
from rss.sphinxapi import SPH_MATCH_ALL, SphinxClient, SPH_ATTR_TIMESTAMP,\
    SPH_MATCH_EXTENDED, SPH_SORT_TIME_SEGMENTS
import sys

import time
from django.contrib.comments.models import Comment
from feedreader.parser import parse_feed_web
from django.views.decorators.csrf import csrf_exempt

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
        
    form = ReportForm()
    
    if request.is_ajax():
        if latest_items.exists():
            return render_to_response('rss/_items.html', 
                              {'latest_items': latest_items},
                              context_instance=RequestContext(request))
        else:
            return HttpResponse(0)
    else:
        return render_to_response('rss/home.html', 
                              {'latest_items': latest_items,'user_feeds':user_feeds,'form':form},
                              context_instance=RequestContext(request))

def user_likes(request, user_id):
    
    try:
        offset = int(request.GET.get('older', 0))
    except ValueError:
        offset = 0
    
    if offset > 0:
        likes = Likes.objects.filter(user=user_id).all().order_by('-id')[offset:offset+30]
    else:
        likes = Likes.objects.filter(user=user_id).all().order_by('-id')[:30]
    lss = []
    for l in likes:
        lss.append(l.item_id)
    latest_items = Item.objects.filter(id__in=lss).all().order_by('-timestamp')[:30]
    
        
    
    try:   
        user_feeds = Subscribe.objects.filter(user=request.user).all()
    except :
        user_feeds = ""
        
    form = ReportForm()
    if request.is_ajax():
        if latest_items.exists():
            return render_to_response('rss/_items.html', 
                              {'latest_items': latest_items,'offset':offset+30},
                              context_instance=RequestContext(request))
        else:
            return HttpResponse(0)
    else:
        return render_to_response('rss/user_likes.html', 
                              {'latest_items': latest_items,'user_feeds':user_feeds,'offset':offset+30,'form':form},
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
    
    form = ReportForm()
    
    if request.is_ajax():
        if latest_items.exists():
            return render_to_response('rss/_items.html', 
                              {'latest_items': latest_items},
                              context_instance=RequestContext(request))
        else:
            return HttpResponse(0)
    else:
        return render_to_response('rss/feed.html', 
                              {'latest_items': latest_items, 'feed':feed,'form':form},
                              context_instance=RequestContext(request))

def feed_item(request, feed_id, item_id):
    feed = Feed.objects.get(pk=feed_id)
    item = get_object_or_404(Item.objects.filter(feed=feed_id,id=item_id)[:1])
    
    #store last view
    Lastview.objects.get_or_create(item=item_id)
    
    latest_items = Item.objects.filter(feed=feed_id).all().extra(where=['timestamp<%s'], params=[item.timestamp]).order_by('-timestamp')[:30]
    form = ReportForm()
    return render_to_response('rss/item.html', 
                              {'item': item, 'feed':feed, 'latest_items': latest_items,'form':form},
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

@csrf_exempt
def subscribe_modal(request):
    if request.is_ajax() and request.method=="POST":
        form = FeedForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            
            feed, created = Feed.objects.get_or_create(url=url,defaults={'creator': request.user})
            if created:
                feed_status = parse_feed_web(feed)
                
                if feed_status == 1:
                    sub, sub_created = Subscribe.objects.get_or_create(user=request.user,feed=feed)
                    
                    if sub_created:
                        feed.followers = feed.followers+1
                        feed.save()
                    
                    data = [{'url':feed.get_absolute_url()}]
                    
                    return HttpResponse(json.dumps(data))
                else:
                    feed.delete()
                    return HttpResponse(0)
            else:
                data = [{'url':feed.get_absolute_url()}]
                    
                return HttpResponse(json.dumps(data))
            
    return HttpResponse(0)
            

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

def search_query(query, offset=0):
    
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
        cl.SetLimits ( offset, limit, max(limit,1000) )
    res = cl.Query ( query, index )
    
    docs =[]
    for item in res['matches']:
        docs.append(item['id'])
    
    return docs

def lastview(request):
    lv=Lastview.objects.all().order_by('-id')[:50]
    docs=[]
    for doc in lv:
        docs.append(int(doc.item))
    print docs
            
    result = Item.objects.filter(id__in=docs).all()
    
    objects = dict([(obj.id, obj) for obj in result])
    sorted_objects = [objects[id] for id in docs]
        
    result = sorted_objects
    
    return render_to_response('rss/lastview.html',
                                  {'latest_items':result},
                                  context_instance=RequestContext(request))
    

def search(request):
    q = request.GET.get('q', '')
    
    if q != '':
        searchObj, created = Search.objects.get_or_create(keyword=q)
        if not created:
            searchObj.count=searchObj.count+1
            searchObj.save()
    
        offset = int(request.GET.get('older', 0))

        docs=search_query(q, offset)
            
        result = Item.objects.filter(id__in=docs).all()
        
        objects = dict([(obj.id, obj) for obj in result])
        sorted_objects = [objects[id] for id in docs]
        
        result = sorted_objects
    
        if request.is_ajax():
            return render_to_response('rss/_items.html',
                                  {'latest_items':result, 'offset':offset+30,'q':q},
                                  context_instance=RequestContext(request))
    
        else:
            return render_to_response('rss/search.html',
                                  {'latest_items':result, 'offset':offset+30,'q':q},
                                  context_instance=RequestContext(request))
    else:
        sObj = Search.objects.filter(accept=1)[:100]
        return render_to_response('rss/tags.html',{'sobj':sObj},context_instance=RequestContext(request))
    
def tag(request, q):
    if q != '':
        q=q.replace('-',' ')
        searchObj, created = Search.objects.get_or_create(keyword=q)
        if not created:
            searchObj.count=searchObj.count+1
            searchObj.save()
    
        offset = int(request.GET.get('older', 0))
        docs=search_query(q, offset)
            
        result = Item.objects.filter(id__in=docs).all()
        
        objects = dict([(obj.id, obj) for obj in result])
        sorted_objects = [objects[id] for id in docs]
        
        result = sorted_objects
    
        if request.is_ajax():
            return render_to_response('rss/_items.html',
                                  {'latest_items':result, 'offset':offset+30,'q':q},
                                  context_instance=RequestContext(request))
    
        else:
            return render_to_response('rss/search.html',
                                  {'latest_items':result, 'offset':offset+30,'q':q},
                                  context_instance=RequestContext(request))
    else:
        sObj = Search.objects.all().order_by('-count')[:100]
        return render_to_response('rss/tags.html',{'sobj':sObj},context_instance=RequestContext(request))

def comment_posted(request):
    if request.GET['c']:
        comment_id = request.GET['c'] #B
        comment = Comment.objects.get( pk=comment_id )
        entry = Item.objects.get(id=comment.object_pk) #C
        if entry:
            return HttpResponseRedirect( entry.get_absolute_url() ) #D
    return HttpResponseRedirect( "/" )    

@login_required
def report(request):

        if request.method=="POST":
            form = ReportForm(request.POST)
            if form.is_valid():
                
                item_id=request.POST['feedId']
                item = Item.objects.get(pk=item_id)
                reported = Report.objects.filter(user=request.user, item=item).count()
                
                if not reported :
                    report = Report()    
                    report.user = request.user
                    report.item = item
                    report.mode = form.Meta
                    report.save()
                    
        return HttpResponseRedirect('/feedreader/')
