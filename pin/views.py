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
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render

from pin.models import Post, Follow, Likes, Category, Comments, Report
from pin.tools import get_request_timestamp, get_request_pid, check_block,\
    get_user_meta, get_user_ip, log_act

from pin.context_processors import is_police

from pin.model_mongo import Ads, PendingPosts

from user_profile.models import Profile
from taggit.models import Tag, TaggedItem

from haystack.query import SearchQuerySet

MEDIA_ROOT = settings.MEDIA_ROOT
REPORT_TYPE = settings.REPORT_TYPE


def home(request):
    log_act("wisgoon.home.view.count")
    pid = get_request_pid(request)
    pl = Post.home_latest(pid=pid)
    arp = []

    last_id = None
    next_url = None

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS_WEB).get(id=pll))
            last_id = pll
        except Exception, e:
            print str(e)
            pass

    if arp:
        next_url = reverse('home') + "?older=" + last_id
        # print next_url

    if request.is_ajax():
        if arp:
            return render(request, 'pin2/_items_2.html', {
                'latest_items': arp,
                'next_url': next_url,
            })
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin2/home.html', {
            'latest_items': arp,
            'next_url': next_url
        })


def search(request):
    row_per_page = 20
    results = []
    query = request.GET.get('q', '')
    offset = int(request.GET.get('offset', 0))

    tags = ['کربلا',
            'حرم',
            'امام',
            'تصاویر_پس_زمینه',
            'رضا_صادقی',
            'مهران_مدیری',
            'سعید_معروف']

    if not query:
        sqs = SearchQuerySet().models(Post)\
            .facet('tags', mincount=10, limit=100)
        # print sqs.facet_counts()

        tags = [t for t in sqs.facet_counts()['fields']['tags']]

        return render(request, 'pin2/tags.html', {
            'tags': tags,
        })

    posts = SearchQuerySet().models(Post)\
        .filter(content__contains=query)[offset:offset + 1 * row_per_page]

    if request.is_ajax():
        return render(request, 'pin2/__search.html', {
            'results': results,
            'posts': posts,
            'query': query,
            'offset': offset + row_per_page,
        })

    return render(request, 'pin2/search.html', {
        'results': results,
        'posts': posts,
        'query': query,
        'offset': offset + row_per_page,
    })


def category_top(request, category_id):
    row_per_page = 20
    cat = get_object_or_404(Category, pk=category_id)
    results = []
    offset = int(request.GET.get('offset', 0))

    posts = SearchQuerySet().models(Post)\
        .filter(category_i=category_id)\
        .order_by('-cnt_like_i')[offset:offset + 1 * row_per_page]

    if request.is_ajax():
        return render(request, 'pin2/__search.html', {
            'results': results,
            'posts': posts,
            'offset': offset + row_per_page,
        })

    return render(request, 'pin2/category_top.html', {
        'results': results,
        'posts': posts,
        'offset': offset + row_per_page,
        'cur_cat': cat
    })


def tags(request, tag_name):
    row_per_page = 20
    results = []
    query = tag_name.replace('_', ' ')
    offset = int(request.GET.get('offset', 0))
    posts = SearchQuerySet().models(Post)\
        .filter(content__contains=query)\
        .order_by('-timestamp_i')[offset:offset + 1 * row_per_page]

    tags = ['کربلا']

    if not query:
        return render(request, 'pin2/tags.html', {
            'tags': tags,
        })

    if request.is_ajax():
        return render(request, 'pin2/__search.html', {
            'results': results,
            'posts': posts,
            'query': query,
            'offset': offset + row_per_page,
        })

    return render(request, 'pin2/tag.html', {
        'results': results,
        'posts': posts,
        'query': query,
        'page_title': tag_name,
        'offset': offset + row_per_page,
    })


def hashtag(request, tag_name):
    row_per_page = 20
    results = []
    query = tag_name
    offset = int(request.GET.get('offset', 0))
    posts = SearchQuerySet().models(Post)\
        .filter(tags=tag_name)\
        .order_by('-timestamp_i')[offset:offset + 1 * row_per_page]

    tags = ['کربلا']

    if not query:
        return render(request, 'pin2/tags.html', {
            'tags': tags,
        })

    if request.is_ajax():
        return render(request, 'pin2/__search.html', {
            'results': results,
            'posts': posts,
            'query': query,
            'offset': offset + row_per_page,
        })

    return render(request, 'pin2/tag.html', {
        'results': results,
        'posts': posts,
        'query': query,
        'page_title': tag_name,
        'offset': offset + row_per_page,
    })


def user_friends(request, user_id):
    user_id = int(user_id)
    row_per_page = 20

    friends = Follow.objects.values_list('following_id', flat=True)\
        .filter(follower_id=user_id).order_by('-id')
    if len(friends) == 0:
        return render(request, 'pin/user_friends_empty.html')
    paginator = Paginator(friends, row_per_page)

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


def absuser_friends(request, user_namefg):
    row_per_page = 20

    user = get_object_or_404(User, username=user_namefg)
    user_id = user.id

    friends = Follow.objects.values_list('following_id', flat=True)\
        .filter(follower_id=user_id).order_by('-id')
    if len(friends) == 0:
        return render(request, 'pin/user_friends_empty.html')
    paginator = Paginator(friends, row_per_page)

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


def user_followers(request, user_id):
    user_id = int(user_id)
    row_per_page = 20

    friends = Follow.objects.values_list('follower_id', flat=True)\
        .filter(following_id=user_id).order_by('-id')
    if len(friends) == 0:
        return render(request, 'pin/user_friends_empty.html')
    paginator = Paginator(friends, row_per_page)

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


def absuser_followers(request, user_namefl):
    row_per_page = 20

    user = get_object_or_404(User, username=user_namefl)
    user_id = user.id

    friends = Follow.objects.values_list('follower_id', flat=True)\
        .filter(following_id=user_id).order_by('-id')
    if len(friends) == 0:
        return render(request, 'pin/user_friends_empty.html')
    paginator = Paginator(friends, row_per_page)

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
    user = get_object_or_404(User, pk=user_id)
    profile = Profile.objects.get(user_id=user_id)

    pid = get_request_pid(request)
    pl = Likes.user_likes(user_id=user_id, pid=pid)
    arp = []

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS_WEB).get(id=pll))
        except:
            pass

    latest_items = arp

    if request.is_ajax():
        if latest_items:
            return render(request,
                          'pin2/_items_2.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin2/user__likes.html',
                      {'latest_items': latest_items,
                       'user_id': user_id,
                       'profile': profile,
                       'cur_user': user})


def absuser_like(request, user_namel):

    user = get_object_or_404(User, username=user_namel)
    user_id = user.id
    profile = Profile.objects.get(user_id=user_id)

    pid = get_request_pid(request)
    pl = Likes.user_likes(user_id=user_id, pid=pid)
    arp = []

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS_WEB).get(id=pll))
        except:
            pass

    latest_items = arp

    user.cnt_follower = Follow.objects.filter(following_id=user.id).count()
    user.cnt_following = Follow.objects.filter(follower_id=user.id).count()

    if request.is_ajax():
        if latest_items:
            return render(request,
                          'pin2/_items_2.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        follow_status = Follow.objects\
            .filter(follower=request.user.id, following=user.id).count()
        return render(request, 'pin2/user__likes.html',
                      {'latest_items': latest_items,
                       'user_id': user_id,
                       'follow_status': follow_status,
                       'profile': profile,
                       'cur_user': user})


def rp(request):
    if request.user.is_superuser:
        posts = Post.objects.all().filter(report__gt=0).order_by('-report')
        for p in posts:
            p.reporters = Report.objects.filter(post_id=p.id)
        return render(request, 'pin2/rp.html', {
            'rps': posts
        })
    else:
        return HttpResponseRedirect(reverse('pin-home'))


# hp = Post.get_hot()
# if hp:
#     latest_items = itertools.chain(hp, latest_items)


def latest_redis(request):
    pid = get_request_pid(request)
    pl = Post.latest(pid=pid)
    arp = []
    last_id = None
    next_url = None

    if request.user.id:
        viewer_id = str(request.user.id)
    else:
        viewer_id = str(get_user_ip(request))

    ad = Ads.get_ad(user_id=viewer_id)
    if ad:
        try:
            if ad.post not in pl:
                pl.append(str(ad.post.id))
        except:
            pass

    for pll in pl:
        try:
            arp.append(Post.objects.get(id=pll))
            last_id = pll
        except:
            pass

    if arp and last_id:
        next_url = reverse('pin-latest') + "?pid=" + last_id

    if request.is_ajax():
        if arp:
            return render(request, 'pin2/_items_2.html', {
                'latest_items': arp,
                'next_url': next_url,
            })
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin2/latest_redis.html', {
            'latest_items': arp,
            'next_url': next_url,
        })


def last_likes(request):
    pl = Post.last_likes()
    arp = []

    for pll in pl:
        try:
            arp.append(Post.objects.get(id=pll))
        except:
            pass

    latest_items = arp

    if request.is_ajax():
        # if latest_items:
        #     return render(request,
        #                   'pin2/_items_2.html',
        #                   {'latest_items': latest_items})
        # else:
        return HttpResponse(0)
    else:
        return render(request, 'pin2/latest_redis.html', {
            'latest_items': latest_items
        })


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

    # auths = Author.objects.order_by('-score')[:30]
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

    if not request.user.is_authenticated:
        if int(cat_id) in [23, 22]:
            return HttpResponse('/')

    cat_id = cat.id
    pid = get_request_pid(request)
    pl = Post.latest(pid=pid, cat_id=cat_id)
    arp = []

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS_WEB).get(id=pll))
            # arp.append(Post.objects.get(id=pll))
        except:
            pass

    latest_items = arp

    if request.is_ajax():
        if latest_items:
            return render(request,
                          'pin2/_items_2.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:
        return render(request,
                      'pin2/category_redis.html',
                      {'latest_items': latest_items, 'cur_cat': cat})


def popular(request, interval=""):
    try:
        offset = int(request.GET.get('offset', 0))
    except ValueError:
        offset = 0

    dt_now = datetime.datetime.now()
    dt_now = dt_now.replace(minute=0, second=0, microsecond=0)

    if interval and interval in ['month', 'lastday', 'lasteigth', 'lastweek']:
        if interval == 'month':
            data_from = dt_now - datetime.timedelta(days=30)
        elif interval == 'lastday':
            data_from = dt_now - datetime.timedelta(days=1)
        elif interval == 'lastweek':
            data_from = dt_now - datetime.timedelta(days=7)
        elif interval == 'lasteigth':
            data_from = dt_now - datetime.timedelta(days=1)

        start_from = mktime(data_from.timetuple())

        posts = SearchQuerySet().models(Post)\
            .filter(timestamp_i__gt=int(start_from))\
            .order_by('-cnt_like_i')[offset:offset + 1 * 20]

    else:
        posts = SearchQuerySet().models(Post)\
            .order_by('-cnt_like_i')[offset:offset + 1 * 20]

    if request.is_ajax():
        return render(request, 'pin2/__search.html',
                      {'posts': posts,
                       'offset': offset + 20})

    else:
        return render(request, 'pin2/popular.html',
                      {'posts': posts,
                       'offset': offset + 20})


def topuser(request):
    cd = cache.get("topuser")
    if not cd:
        top_user = cd

        top_user = Profile.objects.all().order_by('-score')[:152]
        for tu in top_user:
            tu.follow_status = Follow.objects\
                .filter(follower=request.user.id, following=tu.user_id).count()
            print tu.follow_status

        cache.set("topuser", top_user, 86400)
    else:
        top_user = cd

    return render(request, 'pin2/topuser.html', {'top_user': top_user})


def topgroupuser(request):
    tc = cache.get("topgroupuser")
    if not tc:
        cats = Category.objects.all()
        for cat in cats:
            cat.tops = Post.objects.values('user_id')\
                .filter(category_id=cat.id)\
                .annotate(sum_like=Sum('cnt_like'))\
                .order_by('-sum_like')[:4]
            for ut in cat.tops:
                ut['user'] = User.objects.get(pk=ut['user_id'])

        cache.set("topgroupuser", cats, 86400)
    else:
        cats = tc

    return render(request, 'pin/topgroupuser.html', {'cats': cats})


def user(request, user_id, user_name=None):
    user = get_object_or_404(User, pk=user_id)
    profile = Profile.objects.get_or_create(user_id=user_id)

    timestamp = get_request_timestamp(request)
    if timestamp == 0:
        latest_items = Post.objects.only(*Post.NEED_KEYS_WEB).filter(user=user_id)\
            .order_by('-timestamp')[:20]
    else:
        latest_items = Post.objects.only(*Post.NEED_KEYS_WEB).filter(user=user_id)\
            .extra(where=['timestamp<%s'], params=[timestamp])\
            .order_by('-timestamp')[:20]

    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'pin2/_items_2_1.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:

        follow_status = Follow.objects\
            .filter(follower=request.user.id, following=user.id).count()

        return render(request, 'pin2/user.html',
                      {'latest_items': latest_items,
                       'follow_status': follow_status,
                       'user_id': int(user_id),
                       'profile': profile,
                       'cur_user': user})


def absuser(request, user_name=None):
    user = get_object_or_404(User, username=user_name)
    user_id = user.id
    profile = Profile.objects.get_or_create(user_id=user_id)

    timestamp = get_request_timestamp(request)
    if timestamp == 0:
        latest_items = Post.objects.only(*Post.NEED_KEYS_WEB).filter(user=user_id)\
            .order_by('-timestamp')[:20]
    else:
        latest_items = Post.objects.only(*Post.NEED_KEYS_WEB).filter(user=user_id)\
            .extra(where=['timestamp<%s'], params=[timestamp])\
            .order_by('-timestamp')[:20]

    user.cnt_follower = Follow.objects.filter(following_id=user.id).count()
    user.cnt_following = Follow.objects.filter(follower_id=user.id).count()

    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'pin2/_items_2_1.html',
                          {'latest_items': latest_items})
        else:
            return HttpResponse(0)
    else:

        follow_status = Follow.objects\
            .filter(follower=request.user.id, following=user.id).count()

        return render(request, 'pin2/user.html',
                      {'latest_items': latest_items,
                       'follow_status': follow_status,
                       'user_id': int(user_id),
                       'profile': profile,
                       'cur_user': user})


def item(request, item_id):
    enable_cacing = False
    if not request.user.is_authenticated():
        enable_cacing = True
        cd = cache.get("page_v1_%s" % item_id)
        if cd:
            # print "get data from cache"
            # print cd
            return cd
    try:
        post = Post.objects.get(id=item_id)
    except Post.DoesNotExist:
        raise Http404("Post does not exist")

    # from_id = request.GET.get("from", None)
    # if from_id:
    #     # print "from:", from_id
    #     from_id = int(from_id)
    #     try:
    #         p_from = Post.objects.get(pk=from_id)
    #         from models_graph import PostGraph
    #         from_post = PostGraph.get_or_create(post_obj=p_from)
    #         to_post = PostGraph.get_or_create(post_obj=post)
    #         PostGraph.from_to(from_post=from_post, to_post=to_post)

    #     except:
    #         pass

    # p = Post.objects.get(id=item_id)

    post.mlt = {}

    # cache_key_mlt = "mlt:%d" % int(item_id)
    # cache_data_mlt = cache.get(cache_key_mlt)
    # if cache_data_mlt:
    #     post.mlt = cache_data_mlt
    # else:
    #     mlt = SearchQuerySet()\
    #         .models(Post).more_like_this(p)[:30]
    #     cache.set(cache_key_mlt, mlt, 86400)
    #     post.mlt = mlt
    # print post.related

    # if not request.user.is_authenticated:
    #     if post.category_id in [23, 22]:
    #         return render(request, 'pending.html')

    if PendingPosts.is_pending(item_id):
        if not is_police(request, flat=True):
            return render(request, 'pending.html')

    if request.user.is_authenticated():
        if check_block(user_id=post.user_id, blocked_id=request.user.id):
            if not is_police(request, flat=True):
                return HttpResponseRedirect('/')

    post.tag = []

    # pl = Likes.objects.filter(post_id=post.id)[:12]
    from models_redis import LikesRedis
    post.likes = LikesRedis(post_id=post.id)\
        .get_likes(offset=0, limit=12, as_user_object=True)

    # s = SearchQuerySet().models(Post).more_like_this(post)
    # print "seems with:", post.id, s[:5]
    follow_status = 0
    if request.user.is_authenticated():
        follow_status = Follow.objects.filter(follower=request.user.id,
                                              following=post.user.id).count()

    comments_url = reverse('pin-get-comments', args=[post.id])

    if request.is_ajax():
        return render(request, 'pin2/items_inner.html',
                      {'post': post, 'follow_status': follow_status})
    else:
        d = render(request, 'pin2/item.html', {
            'post': post,
            'follow_status': follow_status,
            'comments_url': comments_url,
        }, content_type="text/html")
        if enable_cacing:
            cache.set("page_v1_%s" % item_id, d, 300)

        return d


def get_comments(request, post_id):
    offset = int(request.GET.get('offset', 0))
    comments = Comments.objects.filter(object_pk=post_id)\
        .order_by('-id').only('id', 'user__username', 'user__id', 'comment', 'submit_date')[offset:offset + 1 * 10]

    if len(comments) == 0:
        return HttpResponse(0)

    return render(request, 'pin2/__comments_box.html', {
        'comments': comments
    })


def tag(request, keyword):
    row_per_page = 20

    tag = get_object_or_404(Tag, slug=keyword)
    content_type = ContentType.objects.get_for_model(Post)
    tag_items = TaggedItem.objects.filter(tag_id=tag.id,
                                          content_type=content_type)

    paginator = Paginator(tag_items, row_per_page)

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
    return render(request, 'pin2/policy.html')


def stats(request):
    from model_mongo import MonthlyStats
    ms = MonthlyStats.objects().order_by("-date").limit(30)
    op = {
        'posts': [t.count for t in ms if t.object_type == "post"],
        'comments': [t.count for t in ms if t.object_type == "comment"],
        'likes': [t.count for t in ms if t.object_type == "like"],
        'dates': []
    }
    for m in ms:
        if m.date.day not in op['dates']:
            op['dates'].append(m.date.day)
    print op
    return render(request, 'pin2/stats.html', {'op': op})


def feedback(request):
    return render(request, 'pin2/feedback.html')
