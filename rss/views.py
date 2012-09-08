from django.shortcuts import render_to_response
from rss.models import Item, Feed, Subscribe
from django.template.context import RequestContext
from rss.forms import FeedForm
from django.http import HttpResponseRedirect  #, HttpResponse
from django.contrib.auth.decorators import login_required


def home(request):
    
    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    
    if timestamp == 0:
        latest_items = Item.objects.select_related().all().order_by('-timestamp')[:10]
    else:
        latest_items = Item.objects.select_related().all().extra(where=['timestamp<%s'], params=[timestamp]).order_by('-timestamp')[:10]
    
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
        latest_items = Item.objects.select_related().filter(feed=feed_id).all().order_by('-timestamp')[:10]
    else:
        latest_items = Item.objects.select_related().filter(feed=feed_id).all().extra(where=['timestamp<%s'], params=[timestamp]).order_by('-timestamp')[:10]
    

    
    if request.is_ajax():
        return render_to_response('rss/_items.html', 
                              {'latest_items': latest_items},
                              context_instance=RequestContext(request))
    else:
        return render_to_response('rss/feed.html', 
                              {'latest_items': latest_items},
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






