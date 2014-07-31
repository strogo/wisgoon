# coding: utf-8
from time import mktime
import datetime
import operator
import itertools

from django.conf import settings
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum, F
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from pin.models import Post, Follow, Likes, Category, Comments
from pin.tools import get_request_timestamp, get_request_pid

from user_profile.models import Profile
from taggit.models import Tag, TaggedItem

MEDIA_ROOT = settings.MEDIA_ROOT
REPORT_TYPE = settings.REPORT_TYPE


def home(request):
    timestamp = get_request_timestamp(request)

    if timestamp == 0:
        latest_items = Post.accepted.filter(show_in_default=1)\
            .order_by('-is_ads', '-timestamp')[:20]
    else:
        latest_items = Post.accepted.filter(show_in_default=1)\
            .extra(where=['timestamp<%s'], params=[timestamp])\
            .order_by('-timestamp')[:20]

    if request.is_ajax():
        if latest_items.exists():
            return render(request,
                          'pin/_items.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/home.html', {'latest_items': latest_items})


def search(request):
    results = []
    import pysolr
    solr = pysolr.Solr('http://localhost:8983/solr/wisgoon_user', timeout=10)
    query = request.GET.get('q', '')
    if query:
        q_str = "*%s*" % query
        fq = 'username_s:*%s* name_s:*%s*' % (query, query)
        results = solr.search("*:*", fq=fq, rows=50, sort="score_i desc")

    return render(request, 'pin/search.html', {'results': results})

def user_friends(request, user_id):
    user_id = int(user_id)
    ROW_PER_PAGE = 20

    friends = Follow.objects.values_list('following_id', flat=True)\
        .filter(follower_id=user_id).order_by('-id')
    if len(friends) == 0:
        return render(request, 'pin/user_friends_empty.html')
    paginator = Paginator(friends, ROW_PER_PAGE)

    try:
        offset = int(request.GET.get('older', 1))
    except ValueError:
        offset = 1

    try:
        friends = paginator.page(offset)
    except PageNotAnInteger:
        friends = paginator.page(1)
    except EmptyPage:
        return HttpResponse(0)

    if friends.has_next() is False:
        friends.next_page_number = -1

    friends_list = []
    for l in friends:
        friends_list.append(int(l))

    user_items = User.objects.filter(id__in=friends_list)

    if request.is_ajax():
        if user_items.exists():
            return render(request,
                          'pin/_user_friends.html',
                          {'user_items': user_items,
                           'offset': friends.next_page_number})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/user_friends.html',
                      {'user_items': user_items,
                       'offset': friends.next_page_number,
                       'user_id': user_id})


def user_like(request, user_id):
    user_id = int(user_id)
    ROW_PER_PAGE = 20
    likes_list = []

    likes = Likes.objects.values_list('post_id', flat=True)\
        .filter(user_id=user_id).order_by('-id')

    paginator = Paginator(likes, ROW_PER_PAGE)

    try:
        offset = int(request.GET.get('older', 1))
    except ValueError:
        offset = 1

    try:
        likes = paginator.page(offset)
    except PageNotAnInteger:
        likes = paginator.page(1)
    except EmptyPage:
        return HttpResponse(0)

    if likes.has_next() is False:
        likes.next_page_number = -1

    for l in likes:
        likes_list.append(int(l))

    latest_items = Post.accepted.filter(id__in=likes_list)

    if request.is_ajax():
        if latest_items.exists():
            return render(request,
                          'pin/_items.html',
                          {'latest_items': latest_items,
                           'offset': likes.next_page_number})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/mylike.html',
                      {'latest_items': latest_items,
                       'offset': likes.next_page_number,
                       'user_id': user_id})


# hp = Post.get_hot()
# if hp:
#     latest_items = itertools.chain(hp, latest_items)

def latest_redis(request):
    pid = get_request_pid(request)

    pl = Post.latest(pid=pid)
        
    arp = []
    # latest_items = Post.objects.filter(id__in=pl)
    # latest_items = sorted(latest_items, 
    #                       key=operator.attrgetter('timestamp'),
    #                       reverse=True)

    for pll in pl:
        try:
            arp.append(Post.objects.get(id=pll))
        except:
            pass

    latest_items = arp

    # if timestamp == 0:
    #     latest_items = Post.accepted\
    #         .order_by('-timestamp')[:20]

    #     hp = Post.get_hot()
    #     if hp:
    #         latest_items = itertools.chain(hp, latest_items)
    # else:
    #     latest_items = Post.accepted\
    #         .extra(where=['timestamp<%s'], params=[timestamp])\
    #         .order_by('-timestamp')[:20]

    if request.is_ajax():
        if latest_items:
            return render(request,
                          'pin/_items_2.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/latest_redis.html', {'latest_items': latest_items})

def latest_backup(request):
    timestamp = get_request_timestamp(request)

    if timestamp == 0:
        latest_items = Post.accepted\
            .order_by('-timestamp')[:20]

        hp = Post.get_hot()
        if hp:
            latest_items = itertools.chain(hp, latest_items)
    else:
        latest_items = Post.accepted\
            .extra(where=['timestamp<%s'], params=[timestamp])\
            .order_by('-timestamp')[:20]

    if request.is_ajax():
        if latest_items:
            return render(request,
                          'pin/_items.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/home.html', {'latest_items': latest_items})


def latest_back(request):
    timestamp = get_request_timestamp(request)

    # if timestamp == 0:
    print "timestamp is:", timestamp
    pl = Post.latest(timestamp=timestamp)
    idis = []
    for p in pl:
        idis.append(int(p[1]))
    
    print idis
    latest_items = Post.objects.filter(id__in=idis).order_by('-timestamp')[:20]
    latest_items = sorted(latest_items, 
                          key=operator.attrgetter('timestamp'),
                          reverse=True)
    for li in latest_items:
        print li.id, li.timestamp

    #auths = Author.objects.order_by('-score')[:30]
    # latest_items = sorted(latest_items, 
    #                       key=operator.attrgetter('timestamp'),
    #                       reverse=True)

        # hp = Post.get_hot()
        # if hp:
        #     latest_items = itertools.chain(hp, latest_items)
    # else:
    #     latest_items = Post.accepted\
    #         .extra(where=['timestamp<%s'], params=[timestamp])\
    #         .order_by('-timestamp')[:20]

    if request.is_ajax():
        if latest_items:
            return render(request,
                          'pin/_items.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/home.html', {'latest_items': latest_items})


def category_back(request, cat_id):
    cat = get_object_or_404(Category, pk=cat_id)
    cat_id = cat.id
    timestamp = get_request_timestamp(request)

    if timestamp == 0:
        latest_items = Post.objects.filter(status=1, category=cat_id)\
            .order_by('-is_ads', '-timestamp')[:20]
    else:
        latest_items = Post.objects.filter(status=1, category=cat_id)\
            .extra(where=['timestamp<%s'], params=[timestamp])\
            .order_by('-timestamp')[:20]

    if request.is_ajax():
        if latest_items.exists():
            return render(request,
                          'pin/_items.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        return render(request,
                      'pin/category.html',
                      {'latest_items': latest_items, 'cur_cat': cat})


def category_redis(request, cat_id):
    cat = get_object_or_404(Category, pk=cat_id)
    cat_id = cat.id
    timestamp = get_request_timestamp(request)

    pid = get_request_pid(request)

    pl = Post.latest(pid=pid, cat_id=cat_id)
        
    arp = []
    # latest_items = Post.objects.filter(id__in=pl)
    # latest_items = sorted(latest_items, 
    #                       key=operator.attrgetter('timestamp'),
    #                       reverse=True)

    for pll in pl:
        try:
            arp.append(Post.objects.get(id=pll))
        except:
            pass

    latest_items = arp

    if request.is_ajax():
        if latest_items:
            return render(request,
                          'pin/_items_2.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        return render(request,
                      'pin/category_redis.html',
                      {'latest_items': latest_items, 'cur_cat': cat})


def popular(request, interval=""):
    ROW_PER_PAGE = 20

    if interval and interval in ['month', 'lastday', 'lasteigth', 'lastweek']:
        if interval == 'month':
            data_from = datetime.datetime.now() - datetime.timedelta(days=30)
        elif interval == 'lastday':
            data_from = datetime.datetime.now() - datetime.timedelta(days=1)
        elif interval == 'lastweek':
            data_from = datetime.datetime.now() - datetime.timedelta(days=7)
        elif interval == 'lasteigth':
            data_from = datetime.datetime.now() - datetime.timedelta(hours=8)

        start_from = mktime(data_from.timetuple())
        post_list = Post.objects.filter(status=1)\
            .extra(where=['timestamp>%s'], params=[start_from])\
            .order_by('-cnt_like')

    else:
        post_list = Post.objects.filter(status=1)\
            .order_by('-cnt_like')
    paginator = Paginator(post_list, ROW_PER_PAGE)

    try:
        offset = int(request.GET.get('older', 1))
    except ValueError:
        offset = 1

    try:
        latest_items = paginator.page(offset)
    except PageNotAnInteger:
        latest_items = paginator.page(1)
    except EmptyPage:
        return HttpResponse(0)

    if request.is_ajax():
        return render(request, 'pin/_items.html',
                      {'latest_items': latest_items,
                       'offset': latest_items.next_page_number})

    else:
        return render(request, 'pin/home.html',
                      {'latest_items': latest_items,
                       'offset': latest_items.next_page_number})


def topuser(request):
    top_user = Profile.objects.all().order_by('-score')[:152]

    return render(request, 'pin/topuser.html', {'top_user': top_user})


def topgroupuser(request):
    cats = Category.objects.all()
    for cat in cats:
        cat.tops = Post.objects.values('user_id')\
            .filter(category_id=cat.id)\
            .annotate(sum_like=Sum('cnt_like'))\
            .order_by('-sum_like')[:4]
        for ut in cat.tops:
            ut['user'] = User.objects.get(pk=ut['user_id'])

    return render(request, 'pin/topgroupuser.html', {'cats': cats})


def user(request, user_id, user_name=None):
    user = get_object_or_404(User, pk=user_id)

    profile, created = Profile.objects.get_or_create(user=user)
    if not profile.count_flag:
        profile.user_statics()

    timestamp = get_request_timestamp(request)

    if request.user == user:
        if timestamp == 0:
            latest_items = Post.objects.filter(user=user_id)\
                .order_by('-timestamp')[:20]
        else:
            latest_items = Post.objects.filter(user=user_id)\
                .extra(where=['timestamp<%s'], params=[timestamp])\
                .order_by('-timestamp')[:20]

    else:
        if timestamp == 0:
            latest_items = Post.objects.filter(status=1, user=user_id)\
                .order_by('-timestamp')[:20]
        else:
            latest_items = Post.objects.filter(user=user_id, status=1)\
                .extra(where=['timestamp<%s'], params=[timestamp])\
                .order_by('-timestamp')[:20]

    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'pin/_items.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:

        follow_status = Follow.objects\
            .filter(follower=request.user.id, following=user.id).count()

        return render(request, 'pin/user.html',
                      {'latest_items': latest_items,
                       'follow_status': follow_status,
                       'profile': profile,
                       'cur_user': user})


def item(request, item_id):
    post = get_object_or_404(
        Post.objects.select_related().filter(id=item_id, status=1)[:1])
    #Post.objects.filter(id=item_id).update(view=F('view') + 1)

    post.tag = []

    # if request.user.is_superuser and request.GET.get('ip', None):
    #     post.comments = Comments.objects.filter(object_pk=post)
    #     post.likes = Likes.objects.filter(post=post).order_by('ip')[:10]
    # else:
    post.comments = Comments.objects.filter(object_pk=post)
    str_likers = "web_likes_%s" % post.id
    csl = cache.get(str_likers)
    if csl:
        post.likes = csl
    else:
        pl = Likes.objects.filter(post_id=post.id).values_list('user_id', flat=True)[:12]
        ll = [liker for liker in pl]
        cache.set(str_likers, ll, 86400)
        post.likes = ll

    
    #cache.set("w_likes_"+str(post.id), pp, 30)

    # try:
    #     c_prev = cache.get('prev_post_'+str(post.id))
    #     if c_prev:
    #         post.prev = c_prev
    #     else:
    #         post.prev = Post.objects.filter(status=1)\
    #             .extra(where=['id<%s'], params=[post.id]).order_by('-id')[:1][0]
    #         cache.set('prev_post_'+str(post.id), post.prev, 3600)

    #     c_next = cache.get('next_post_'+ str(post.id))
    #     if c_next:
    #         post.next = c_next
    #     else:
    #         post.next = Post.objects.filter(status=1)\
    #             .extra(where=['id>%s'], params=[post.id]).order_by('id')[:1][0]
    #         cache.set("next_post_"+str(post.id), post.next, 86400)
    # except:
    #     pass

    if request.user.is_authenticated:
        follow_status = Follow.objects.filter(follower=request.user.id,
                                          following=post.user.id).count()

    if request.is_ajax():
        return render(request, 'pin/item_inner.html',
                      {'post': post, 'follow_status': follow_status})
    else:
        return render(request, 'pin/item.html',
                      {'post': post, 'follow_status': follow_status})


def tag(request, keyword):
    ROW_PER_PAGE = 20

    tag = get_object_or_404(Tag, slug=keyword)
    content_type = ContentType.objects.get_for_model(Post)
    tag_items = TaggedItem.objects.filter(tag_id=tag.id,
                                          content_type=content_type)

    paginator = Paginator(tag_items, ROW_PER_PAGE)

    try:
        offset = int(request.GET.get('older', 1))
    except ValueError:
        offset = 1

    try:
        tag_items = paginator.page(offset)
    except PageNotAnInteger:
        tag_items = paginator.page(1)
    except EmptyPage:
        return HttpResponse(0)

    s = []
    for t in tag_items:
        s.append(t.object_id)

    if tag_items.has_next() is False:
        tag_items.next_page_number = -1
    latest_items = Post.objects.filter(id__in=s, status=1).all()

    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'pin/_items.html',
                          {'latest_items': latest_items,
                           'offset': tag_items.next_page_number})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/tag.html',
                      {'latest_items': latest_items,
                       'tag': tag,
                       'offset': tag_items.next_page_number})


def policy(request):
    return render(request, 'pin/policy.html')
