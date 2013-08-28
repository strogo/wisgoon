# -*- coding: utf-8 -*- 
import time
import json
from urllib import quote
import sys
import simplejson
import datetime

from django.shortcuts import render_to_response, get_object_or_404, render
from django.template.context import RequestContext
from django.http import HttpResponseRedirect  #, HttpResponse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.core.urlresolvers import reverse
from rss.sphinxapi import SphinxClient, SPH_MATCH_EXTENDED, \
        SPH_SORT_ATTR_DESC, SPH_MATCH_ANY, SPH_GROUPBY_DAY, SPH_SORT_ATTR_ASC

from django.template.loader import render_to_string
from django.utils.http import urlencode
from django.contrib.comments.models import Comment
from feedreader.parser import parse_feed_web
from django.views.decorators.csrf import csrf_exempt

from rss.models import Item, Feed, Subscribe, Likes ,Report, Search, Lastview, ItemExtra, Category
from rss.utils import clean_words
from rss.forms import FeedForm, ReportForm

MAX_PER_PAGE = 10

def category(request):
    cats = Category.objects.all()
    for cat in cats:
        cat_feeds = Feed.objects.filter(category=cat)
        cat_idis = [int(feed.id) for feed in cat_feeds]
        cat.items = Item.objects.filter(feed__in=cat_idis).order_by('-id')[:5]
            
    return render(request, 'rss/category.html', {'cats':cats})

def older(request):
    try:
        id = int(request.GET.get('older', 0))
    except ValueError:
        id = 0
    
    if id != 0:
        latest_items = Item.objects.all().extra(where=['id<%s'], params=[id]).order_by('-id')[:MAX_PER_PAGE]
    
        if request.is_ajax():
            if latest_items.exists():
#                html = render_to_string("rss/_items.html", {'latest_items': latest_items})
#                serialized_data = simplejson.dumps({"html": html,'lastid':latest_items[0].id})
#                return HttpResponse(serialized_data, mimetype="application/json")
                return render(request,'rss/_items.html', {'latest_items': latest_items})
            else:
                return HttpResponse(0)
    return HttpResponse(0)

def home(request):
    
    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    
    if timestamp == 0:
        latest_items = Item.objects.all().order_by('-timestamp')[:MAX_PER_PAGE]
    else:
        latest_items = Item.objects.all().extra(where=['id<%s'], params=[int(timestamp)]).order_by('-id')[:MAX_PER_PAGE]
    
    try:   
        user_feeds = Subscribe.objects.filter(user=request.user).all()
    except :
        user_feeds = ""
        
    form = ReportForm()
    
    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'rss/_items.html', {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'rss/home.html', {'latest_items': latest_items,'user_feeds':user_feeds,'form':form})

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
        return render(request, 'rss/user_likes.html', 
                              {'latest_items': latest_items,'user_feeds':user_feeds,'offset':offset+30,'form':form})

def get_feed_range(feed_id=0):
    feed_id = int(feed_id)

    sc = SphinxClient()
    sc.SetServer('localhost',9312)
    sc.SetGroupBy('date_added',SPH_GROUPBY_DAY)
    if feed_id > 0:
        sc.SetFilter('feed_id',[feed_id])
    sc.SetLimits(0,10)

    return sc.Query('')
     
def feed(request, feed_id, older=0):
    
    timestamp = int(older)
    
    feed = Feed.objects.get(pk=feed_id)
    
    if timestamp == 0:
        latest_items = Item.objects.filter(feed=feed_id).all().order_by('-id')[:MAX_PER_PAGE]
    else:
        endtimestamp = get_older_days_time(timestamp, 5)
        #latest_items = Item.objects.filter(feed=feed_id, timestamp__range=(endtimestamp, timestamp-1)).all().order_by('-timestamp')[:MAX_PER_PAGE]
        latest_items = Item.objects.filter(feed=feed_id).extra(where=['id<%s'], params=[timestamp]).all().order_by('-id')[:MAX_PER_PAGE]
    if not latest_items:
        if request.is_ajax():
            return HttpResponse(0)
        else:
            raise Http404
    
    for li in latest_items:
        lrow = li
    
    older_url = reverse('rss-feed-older', args=[feed_id, lrow.id])
    
    form = ReportForm()
    
    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'rss/_items.html', {'latest_items': latest_items, 'older_url': older_url})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'rss/feed.html', {'latest_items': latest_items, 'feed':feed,'form':form , 'older_url': older_url})

def get_older_days_time(timestamp, days=10):
    now = datetime.datetime.fromtimestamp(timestamp)
    lm = now - datetime.timedelta(days=days)
    endtimestamp = time.mktime(lm.timetuple())
    return endtimestamp

def feed_item(request, feed_id, item_id):
    try:
        feed = Feed.objects.get(pk=feed_id)
    except Feed.DoesNotExist:
        raise Http404
    item = get_object_or_404(Item.objects.filter(feed=feed_id,id=item_id)[:1])
       
    docs=search_query( clean_words(item.title), mode=SPH_MATCH_ANY, limit=10)
    if docs:
        if int(item_id) in docs:
            docs.remove(int(item_id))
        result = Item.objects.filter(id__in=docs).all()
            
        objects = dict([(obj.id, obj) for obj in result])
        sorted_objects = [objects[id] for id in docs]
        
        related_posts = sorted_objects
    else:
        related_posts = []
    #store last view
    Lastview.objects.get_or_create(item=item_id)
    
    endtimestamp = get_older_days_time(item.timestamp,5)

    latest_items = Item.objects.filter(feed=feed_id).extra(where=['id<%s'], params=[int(item_id)]).all().order_by('-id')[:10]
    
    for li in latest_items:
        lrow = li
    
    try:
        older_url = reverse('rss-feed-older', args=[feed_id, lrow.id])
    except:
        older_url = ""
    
    form = ReportForm()
    return render(request, 'rss/item.html', 
                              {'item': item, 'feed':feed, 'latest_items': latest_items,'form':form,'older_url': older_url
                              ,'related_posts':related_posts})

def feed_item_goto(request, item_id):
    item = get_object_or_404(Item.objects.filter(id=item_id)[:1])
    
    #store last view
    Lastview.objects.get_or_create(item=item_id)
    
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

def store_extra(item_id, tag, time):
    upex = ItemExtra.objects(item_id=item_id)
    if not upex:
        item_ext = ItemExtra(item_id=item_id, tags=[tag], time=time)
        item_ext.save()
    else:
        upex = ItemExtra.objects(item_id=item_id, tags__nin=[tag]).update_one(push__tags=tag)

def search_query(query, offset=0, sort=1, has_image=-1, mode=SPH_MATCH_EXTENDED, limit=30):
    
    host = 'localhost'
    port = 9312
    index = 'rss_item'
    filtercol = 'group_id'
    filtervals = []
    sortby = '-@weights'
    groupby = 'id'
    groupsort = '@group desc'
    
    # do query
    cl = SphinxClient()
    cl.SetServer ( host, port )
    cl.SetWeights ( [100, 1] )
    
    if sort==1:
        """ default order by relation """
        pass
    elif sort==2:
        """ order to date  """
        cl.SetSortMode(SPH_SORT_ATTR_DESC, 'date_added')
    
    if has_image != -1 and  has_image in (0,1):
        cl.SetFilter('has_image', [has_image])

    
#    print "has image: ", has_image
    
    cl.SetMatchMode ( mode )

    #cl.SetSortMode(SPH_SORT_TIME_SEGMENTS)
    if limit:
        cl.SetLimits ( offset, limit, max(limit,1000) )
    res = cl.Query ( query, index )
    
    docs =[]
    if res:
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
        try:
            sort = int(request.GET.get('sort', 1))
        except:
            sort = 1
            
        try:
            has_image = int(request.GET.get('has_image', -1))
        except:
            has_image = -1

        docs=search_query(q, offset, sort, has_image)
            
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
                                  {'latest_items':result, 'offset':offset+30,'q':q, 'sort':sort, 'has_image':has_image},
                                  context_instance=RequestContext(request))
    else:
        sObj = Search.objects.filter(accept=1)
        return render_to_response('rss/tags.html',{'sobj':sObj},context_instance=RequestContext(request))
    
def tag(request, q, older=0):
    if q != '':
        tag_original = q
        q=q.replace('-',' ')
        save_keyword= True
        
        try:
            searchObj = Search.objects.get(keyword=q)
            
            searchObj.count=searchObj.count+1
            searchObj.save()
        except Search.DoesNotExist:
            save_keyword= False
            
        offset = int(older)
        docs=search_query(q, offset, sort=2)
        if not docs:
            if request.is_ajax():
                return HttpResponse(0)
            else:
                raise Http404
            
        result = Item.objects.filter(id__in=docs).all()
        
        objects = dict([(obj.id, obj) for obj in result])
        sorted_objects = [objects[id] for id in docs]
        
        result = sorted_objects
        older_url = ""
        if save_keyword:
            for row in result:
                store_extra(row.id, tag_original, row.timestamp)
        
        #tag_in_url = quote(tag_original.encode('utf-8'))
        #tag_in_url = tag_original
        #older_url = reverse('tag-older', args=[tag_in_url, offset+30])
        older_url = ""
    
        if request.is_ajax():
            return render_to_response('rss/_tag_items.html',
                                  {'latest_items':result, 'offset':offset+30,'q':q, "older_url": older_url},
                                  context_instance=RequestContext(request))
    
        else:
            return render_to_response('rss/tagview.html',
                                  {'latest_items':result, 'offset':offset+30,'q':q, "older_url": older_url},
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

def favicon(request):
    try:
        url = request.GET.get('url', '')
    except :
        pass
    return HttpResponse(url)























