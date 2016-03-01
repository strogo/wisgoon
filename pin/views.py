# coding: utf-8
from time import mktime, time
import json
import datetime
import operator
import itertools

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache
from django.contrib.contenttypes.models import ContentType
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from pin.models import Post, Follow, Likes, Category, Comments, Report,\
    Results
from pin.tools import get_request_timestamp, get_request_pid, check_block,\
    get_user_ip, get_delta_timestamp

from pin.context_processors import is_police

from pin.model_mongo import Ads
from pin.models_redis import LikesRedis

from pin.api6.tools import post_item_json

# from daddy_avatar.templatetags import daddy_avatar
from user_profile.models import Profile
# from taggit.models import Tag, TaggedItem

from haystack.query import SearchQuerySet

User = get_user_model()
MEDIA_ROOT = settings.MEDIA_ROOT
REPORT_TYPE = settings.REPORT_TYPE


def home(request):
    pid = get_request_pid(request)
    cache_str = "page:home:%s" % str(pid)
    enable_cacing = False
    if not request.user.is_authenticated():
        enable_cacing = True
        cd = cache.get(cache_str)
        if cd:
            return cd
    pl = Post.home_latest(pid=pid)
    arp = []

    last_id = None
    next_url = None

    for pll in pl:
        try:
            post_id = int(pll)
            post_item = post_item_json(post_id=post_id, cur_user_id=request.user.id)
            arp.append(post_item)
            # arp.append(Post.objects.only(*Post.NEED_KEYS_WEB).get(id=pll))
            last_id = pll
        except Exception, e:
            print str(e), "pin views line 63"
            pass

    if arp:
        next_url = reverse('home') + "?older=" + last_id
        # print next_url

    response_data = HttpResponse(0)

    if request.is_ajax():
        if arp:
            response_data = render(request, 'pin2/_items_2_v6.html', {
                'latest_items': arp,
                'next_url': next_url,
            })
        else:
            response_data = HttpResponse(0)
    else:
        response_data = render(request, 'pin2/home_v6.html', {
            'latest_items': arp,
            'next_url': next_url,
            'page': 'home'
        })

    if enable_cacing:
        cache.set(cache_str, response_data, 300)

    return response_data


def leaderboard(request):
    leaders = LikesRedis().get_leaderboards()
    leaders_list = []
    for leader in leaders:
        o = {}
        user_id = int(leader[0])
        user_score = leader[1]
        o['sum_like'] = int(user_score)
        u = User.objects.get(id=user_id)
        o['user'] = u
        leaders_list.append(o)

    return render(request, "pin2/topmonthlyuser.html", {
        'leaders': leaders_list
    })


def search(request):
    row_per_page = 20
    results = []
    posts = []
    facets = {}
    query = request.GET.get('q', '')
    offset = int(request.GET.get('offset', 0))

    if query:
        posts = SearchQuerySet().models(Post)\
            .filter(content__contains=query)[offset:offset + 1 * row_per_page]
    else:
        today_stamp = get_delta_timestamp(days=0)
        week_statmp = get_delta_timestamp(days=7)
        month_statmp = get_delta_timestamp(days=30)

        cur_time = int(time())

        facets['facet_all'] = SearchQuerySet().models(Post)\
            .facet('tags', limit=6)

        facets['facet_today'] = SearchQuerySet().models(Post)\
            .narrow("timestamp_i:[{} TO {}]".format(today_stamp, cur_time))\
            .facet('tags', limit=6)

        facets['facet_week'] = SearchQuerySet().models(Post)\
            .narrow("timestamp_i:[{} TO {}]".format(week_statmp, cur_time))\
            .facet('tags', limit=6)

        facets['facet_month'] = SearchQuerySet().models(Post)\
            .narrow("timestamp_i:[{} TO {}]".format(month_statmp, cur_time))\
            .facet('tags', limit=6)

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
        'facets': facets,
    })


def result(request, label):
    try:
        r = Results.objects.get(label=label)
    except Results.DoesNotExist:
        raise Http404

    row_per_page = 20
    results = []
    query = request.GET.get('q', '')
    offset = int(request.GET.get('older', 0))

    posts = SearchQuerySet().models(Post)\
        .filter(content__contains=r.get_label_text())\
        .order_by('-timestamp_i')[offset:offset + 1 * row_per_page]

    if request.is_ajax():
        return render(request, 'pin2/__search.html', {
            'results': results,
            'posts': posts,
            'query': query,
            'r': r,
            'offset': offset + row_per_page,
        })

    return render(request, 'pin2/result.html', {
        'results': results,
        'posts': posts,
        'query': query,
        'r': r,
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

    if query in [u'عروس', u'عاشقانه'] and not request.user.is_authenticated():
        return render(request, 'pin2/samandehi.html')

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
    raise Http404
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


@csrf_exempt
def absuser_following(request, user_namefg):
    # row_per_page = 20
    user = get_object_or_404(User, username=user_namefg)
    user_id = int(user.id)
    profile, created = Profile.objects.get_or_create(user_id=user_id)
    older = request.POST.get('older', False)

    if older:
        following = Follow.objects\
            .filter(follower_id=user_id, id__lt=older).order_by('-id')[:16]
    else:
        following = Follow.objects.filter(follower_id=user_id).order_by('-id')[:16]

    if request.is_ajax():
        if following.exists():
            return render(request, 'pin2/_user_following.html', {
                'user_items': following,
                'user': user
            })
        else:
            return HttpResponse(0)
    else:
        if request.user.id:
            follow_status = Follow.objects.filter(follower=request.user.id,
                                                  following=user.id).exists()
            following_status = Follow.objects.filter(following=request.user.id,
                                                     follower=user.id).exists()
        else:
            follow_status = 0
            following_status = 0

        return render(request, 'pin2/user_following.html', {
            'user_items': following,
            'page': 'user_following',
            'profile': profile,
            'follow_status': follow_status,
            'following_status': following_status,
            'user_id': user_id,
            'user': user

        })


def user_followers(request, user_id):
    raise Http404
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


@csrf_exempt
def absuser_followers(request, user_namefl):

    user = get_object_or_404(User, username=user_namefl)
    user_id = user.id
    profile, created = Profile.objects.get_or_create(user_id=user_id)
    older = request.POST.get('older', False)
    if older:
        friends = Follow.objects.filter(following_id=user_id, id__lt=older).order_by('-id')[:16]
    else:
        friends = Follow.objects.filter(following_id=user_id).order_by('-id')[:16]
    if request.is_ajax():
        if friends.exists():
            return render(request, 'pin2/_user_followers.html', {
                'user_items': friends,
                'user': user
            })
        else:
            return HttpResponse(0)
    else:

        if request.user.id:
            follow_status = Follow.objects.filter(follower=request.user.id,
                                                  following=user.id).exists()
            following_status = Follow.objects.filter(following=request.user.id,
                                                     follower=user.id).exists()
        else:
            follow_status = 0
            following_status = 0

        return render(request, 'pin2/user_followers.html', {
            'user_items': friends,
            'user_id': int(user_id),
            'page': 'user_follower',
            'profile': profile,
            'follow_status': follow_status,
            'following_status': following_status,
            'user': user
        })


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
                       'page': "user_like",
                       'profile': profile,
                       'cur_user': user})


def absuser_like(request, user_namel):
    user = get_object_or_404(User, username=user_namel)
    user_id = user.id
    profile, created = Profile.objects.get_or_create(user_id=user_id)
    if profile.banned:
        return render(request, 'pin2/samandehi.html')

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
        # follow_status = Follow.objects\
        #     .filter(follower=request.user.id, following=user_id).count()
        if request.user.id:
            follow_status = Follow.objects.filter(follower=request.user.id,
                                                  following=user.id).exists()
            following_status = Follow.objects.filter(following=request.user.id,
                                                     follower=user.id).exists()
        else:
            follow_status = 0
            following_status = 0
        return render(request, 'pin2/user__likes.html', {
            'latest_items': latest_items,
            'user_id': user_id,
            'follow_status': follow_status,
            'following_status': following_status,
            'profile': profile,
            'page': "user_like"
        })


def rp(request):
    if request.user.is_superuser:
        posts = Post.objects.select_related().filter(report__gt=0)\
            .order_by('-report')[:50]
        for p in posts:
            p.reporters = Report.objects.select_related()\
                .filter(post_id=p.id)
        return render(request, 'pin2/rp.html', {
            'page': 'rp',
            'rps': posts
        })
    else:
        return HttpResponseRedirect(reverse('pin-home'))


# hp = Post.get_hot()
# if hp:
#     latest_items = itertools.chain(hp, latest_items)


def latest_redis(request):
    pid = get_request_pid(request)
    cache_str = "page:latest:%s" % str(pid)
    # print "cache str:", cache_str
    enable_cacing = False
    if not request.user.is_authenticated():
        enable_cacing = True
        cd = cache.get(cache_str)
        if cd:
            # print "showing data from cache"
            return cd

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
            pll_id = int(pll)
            arp.append(post_item_json(post_id=pll_id,
                                      cur_user_id=request.user.id))
            # arp.append(Post.objects.only(*Post.NEED_KEYS_WEB).get(id=pll))
            last_id = pll
        except Exception, e:
            raise
            print str(e)
            pass

    if arp and last_id:
        next_url = reverse('pin-latest') + "?pid=" + last_id

    response_data = HttpResponse(0)

    if request.is_ajax():
        if arp:
            response_data = render(request, 'pin2/_items_2_v6.html', {
                'latest_items': arp,
                'next_url': next_url,
            })
        else:
            response_data = HttpResponse(0)
    else:
        response_data = render(request, 'pin2/latest_redis.html', {
            'latest_items': arp,
            'page': 'latest',
            'next_url': next_url,
        })
    if enable_cacing:
        cache.set(cache_str, response_data, 300)

    return response_data


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
    top_user = Profile.objects.all().order_by('-score')[:48]
    for tu in top_user:
        tu.follow_status = Follow.objects\
            .filter(follower=request.user.id, following=tu.user_id).count()
        print tu.follow_status

    return render(request, 'pin2/topuser.html', {'top_user': top_user})


def topgroupuser(request):
    # tc = cache.get("topgroupuser")
    # if not tc:
    cats = Category.objects.all()
    for cat in cats:
        cat.tops = []
        leaders = LikesRedis().get_leaderboards_groups(category=cat.id)
        leaders_list = []
        for leader in leaders:
            o = {}
            user_id = int(leader[0])
            user_score = leader[1]
            o['sum_like'] = int(user_score)
            u = User.objects.get(id=user_id)
            o['user'] = u
            cat.tops.append(o)

            # cat.tops = Post.objects.values('user_id')\
            #     .filter(category_id=cat.id)\
            #     .annotate(sum_like=Sum('cnt_like'))\
            #     .order_by('-sum_like')[:4]
            # for ut in cat.tops:
            #     ut['user'] = User.objects.get(pk=ut['user_id'])

        # cache.set("topgroupuser", cats, 86400)
    # else:
        # cats = tc

    return render(request, 'pin2/topgroupuser.html', {'cats': cats})


def user(request, user_id, user_name=None):
    user = get_object_or_404(User, pk=user_id)
    return HttpResponseRedirect(reverse('pin-absuser', args=[user.username]))
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
    try:
        user = User.objects.only('id').get(username=user_name)
    except User.DoesNotExist:
        raise Http404

    user_id = user.id

    try:
        profile = Profile.objects.only('banned', 'user', 'score', 'cnt_post', 'website', 'credit', 'level', 'bio').get(user_id=user_id)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user_id=user_id)

    if profile.banned and not request.user.is_authenticated():
        return render(request, 'pin2/samandehi.html')

    ban_by_admin = False
    if request.user.is_superuser and not user.is_active:
        from pin.models import Log
        ban_by_admin = Log.objects.filter(object_id=user_id, action=Log.BAN_ADMIN, content_type=Log.USER).order_by('-id')
        if ban_by_admin:
            ban_by_admin = ban_by_admin[0].text

    timestamp = get_request_timestamp(request)
    if timestamp == 0:
        latest_items = Post.objects.only(*Post.NEED_KEYS_WEB).filter(user=user_id)\
            .order_by('-timestamp')[:20]
    else:
        latest_items = Post.objects.only(*Post.NEED_KEYS_WEB).filter(user=user_id)\
            .extra(where=['timestamp<%s'], params=[timestamp])\
            .order_by('-timestamp')[:20]

    profile.cnt_follower = Follow.objects.filter(following_id=user.id).count()
    profile.cnt_following = Follow.objects.filter(follower_id=user.id).count()

    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'pin2/_items_2_1.html', {
                'latest_items': latest_items
            })
        else:
            return HttpResponse(0)
    else:
        if request.user.id:
            follow_status = Follow.objects.filter(follower=request.user.id,
                                                  following=user.id).exists()
            following_status = Follow.objects.filter(following=request.user.id,
                                                     follower=user.id).exists()
        else:
            follow_status = 0
            following_status = 0

        return render(request, 'pin2/user.html', {
            'latest_items': latest_items,
            'follow_status': follow_status,
            'following_status': following_status,
            'ban_by_admin': ban_by_admin,
            'user_id': int(user_id),
            'profile': profile,
        })


def item(request, item_id):
    from pin.model_mongo import MonthlyStats
    MonthlyStats.log_hit(object_type=MonthlyStats.VIEW)

    enable_cacing = False
    if not request.user.is_authenticated():
        enable_cacing = True
        cd = cache.get("page_v1_%s" % item_id)
        if cd:
            return cd
    try:
        post = Post.objects.get(id=item_id)
    except Post.DoesNotExist:
        raise Http404("Post does not exist")

    mlts = []

    post.mlt = mlts

    if post.is_pending():
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
        .get_likes(offset=0, limit=6, as_user_object=True)

    # s = SearchQuerySet().models(Post).more_like_this(post)
    # print "seems with:", post.id, s[:5]
    follow_status = 0
    if request.user.is_authenticated():
        follow_status = Follow.objects.filter(follower=request.user.id,
                                              following=post.user.id).count()

    comments_url = reverse('pin-get-comments', args=[post.id])
    related_url = reverse('pin-item-related', args=[post.id])

    if request.is_ajax():
        return render(request, 'pin2/items_inner.html',
                      {'post': post, 'follow_status': follow_status})
    else:
        d = render(request, 'pin2/item.html', {
            'post': post,
            'follow_status': follow_status,
            'comments_url': comments_url,
            'related_url': related_url,
        }, content_type="text/html")
        if enable_cacing:
            cache.set("page_v1_%s" % item_id, d, 300)

        return d


def post_likers(request, post_id, offset):
    from models_redis import LikesRedis
    from pin.api6.tools import get_simple_user_object
    likers = LikesRedis(post_id=int(post_id))\
        .get_likes(offset=int(offset), limit=10)

    likers_list = []
    for u in likers:
        u = {
            'user': get_simple_user_object(int(u), request.user.id)
        }
        likers_list.append(u)
    data = {
        'status': True,
        'likers': likers_list
    }

    return HttpResponse(json.dumps(data), content_type='application/json')


def item_related(request, item_id):
    enable_caching = False

    if request.is_ajax():
        cache_key = "rel:v1:ajax:%s" % item_id
    else:
        cache_key = "rel:v1:%s" % item_id

    if not request.user.is_authenticated():
        enable_caching = True
        cd = cache.get(cache_key)
        if cd:
            return cd
    try:
        post = Post.objects.get(id=item_id)
    except Post.DoesNotExist:
        raise Http404("Post does not exist")

    mlt = SearchQuerySet()\
        .models(Post).more_like_this(post)[:30]

    idis = []
    for pmlt in mlt:
        idis.append(pmlt.pk)

    post.mlt = Post.objects.filter(id__in=idis).only(*Post.NEED_KEYS_WEB)

    if request.is_ajax():
        d = render(request, 'pin2/_items_related.html', {
            'post': post
        })
    else:
        d = render(request, 'pin2/item_related.html', {
            'post': post,
        }, content_type="text/html")

    if enable_caching:
        cache.set(cache_key, d, 3600)

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


# def tag(request, keyword):
#     row_per_page = 20

#     tag = get_object_or_404(Tag, slug=keyword)
#     content_type = ContentType.objects.get_for_model(Post)
#     tag_items = TaggedItem.objects.filter(tag_id=tag.id,
#                                           content_type=content_type)

#     paginator = Paginator(tag_items, row_per_page)

#     try:
#         offset = int(request.GET.get('older', 1))
#     except ValueError:
#         offset = 1

#     try:
#         tag_items = paginator.page(offset)
#     except PageNotAnInteger:
#         tag_items = paginator.page(1)
#     except EmptyPage:
#         return HttpResponse(0)

#     s = []
#     for t in tag_items:
#         s.append(t.object_id)

#     if tag_items.has_next() is False:
#         tag_items.next_page_number = -1
#     latest_items = Post.objects.filter(id__in=s).all()

#     if request.is_ajax():
#         if latest_items.exists():
#             return render(request, 'pin/_items.html',
#                           {'latest_items': latest_items,
#                            'offset': tag_items.next_page_number})
#         else:
#             return HttpResponse(0)
#     else:
#         return render(request, 'pin/tag.html',
#                       {'latest_items': latest_items,
#                        'tag': tag,
#                        'offset': tag_items.next_page_number})


def policy(request):
    return render(request, 'pin2/statics/policy.html', {'page': 'policy'})


def policy_for_mobile(request):
    return render(request, 'pin2/statics/policy_for_mobile.html')


def about_us(request):
    return render(request, 'pin2/statics/about_us.html', {'page': 'about_us'})


def about_us_for_mobile(request):
    return render(request, 'pin2/statics/about_us_for_mobile.html')


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
    return render(request, 'pin2/statics/feedback.html', {'page': 'feedback'})
