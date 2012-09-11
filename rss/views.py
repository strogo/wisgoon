# -*- coding: utf8 -*- 

from django.shortcuts import render_to_response, get_object_or_404
from rss.models import Item, Feed, Subscribe
from django.template.context import RequestContext
from rss.forms import FeedForm
from django.http import HttpResponseRedirect  #, HttpResponse
from django.contrib.auth.decorators import login_required
import lxml.html
import re
from sorl.thumbnail.shortcuts import get_thumbnail
from urllib2 import HTTPError

def remove_img_tags(data):
    p = re.compile(r'<img.*?>')
    data = p.sub('', data)

    p = re.compile(r'<img.*?/>')
    data = p.sub('', data)
    
    return data
    
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
        
    for item in latest_items:
        item.images = []
        if item.description != '':
            tree = lxml.html.fromstring(item.description)
            for images in tree.xpath("//img/@src"):
                try:
                    item.images.append(get_thumbnail(images, '192'))
                    break
                except HTTPError:
                    pass
                
            item.description = remove_img_tags(lxml.html.tostring(tree, encoding='utf-8'))
                
            #item.images = images
        
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
        latest_items = Item.objects.select_related().filter(feed=feed_id).all().order_by('-timestamp')[:30]
    else:
        latest_items = Item.objects.select_related().filter(feed=feed_id).all().extra(where=['timestamp<%s'], params=[timestamp]).order_by('-timestamp')[:30]
    
    for item in latest_items:
        item.images = []
        if item.description != '':
            tree = lxml.html.fromstring(item.description)
            for images in tree.xpath("//img/@src"):
                try:
                    item.images.append(get_thumbnail(images, '192'))
                    break
                except HTTPError:
                    pass
                
            item.description = remove_img_tags(lxml.html.tostring(tree, encoding='utf-8'))
        
    if request.is_ajax():
        return render_to_response('rss/_items.html', 
                              {'latest_items': latest_items},
                              context_instance=RequestContext(request))
    else:
        return render_to_response('rss/feed.html', 
                              {'latest_items': latest_items},
                              context_instance=RequestContext(request))

def feed_item(request, feed_id, item_id):
    item = get_object_or_404(Item.objects.filter(feed=feed_id,id=item_id)[:1])
    
    return render_to_response('rss/item.html', 
                              {'item': item},
                              context_instance=RequestContext(request))

        
    

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






