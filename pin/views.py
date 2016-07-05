# coding: utf-8
from time import mktime, time
import json
import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.cache import cache
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from pin.models import Post, Follow, Likes, Category, Comments, Results
from pin.tools import get_request_timestamp, get_request_pid, check_block,\
    get_user_ip, get_delta_timestamp, AuthCache

from pin.model_mongo import Ads, MonthlyStats
from pin.models_redis import LikesRedis

from pin.api6.tools import post_item_json

from user_profile.models import Profile

from haystack.query import SearchQuerySet

User = get_user_model()
MEDIA_ROOT = settings.MEDIA_ROOT
REPORT_TYPE = settings.REPORT_TYPE


def home(request):
    pid = get_request_pid(request)
    pl = Post.home_latest(pid=pid)
    arp = []

    last_id = None
    next_url = None

    for pll in pl:
        pid = int(pll)
        post_item = post_item_json(post_id=pid, cur_user_id=request.user.id)
        if post_item:
            if not check_block(user_id=post_item['user']['id'], blocked_id=request.user.id):
                arp.append(post_item)
        last_id = pll

    if arp:
        next_url = reverse('home') + "?older=" + last_id

    if request.is_ajax():
        if arp:
            return render(request, 'pin2/_items_2_v6.html', {
                'latest_items': arp,
                'cls': 'new_items',
                'next_url': next_url,
            })
        else:
            return HttpResponse(0)

    return render(request, 'pin2/home_v6.html', {
        'latest_items': arp,
        'cls': 'new_items',
        'next_url': next_url,
        'page': 'home'
    })


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
        post_queryset = SearchQuerySet().models(Post)\
            .filter(content__contains=query)[offset:offset + 1 * row_per_page]

        for post in post_queryset:
            # if check_block(user_id=post.user.id, blocked_id=request.user.id):
            ob = post_item_json(post_id=post.pk, cur_user_id=request.user.id)
            if ob:
                posts.append(ob)
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

    ps = []
    for post in posts:
        if not check_block(user_id=post.user.id, blocked_id=request.user.id):
            ob = post_item_json(post.pk)
            if ob:
                ps.append(ob)
    # ps = [post_item_json(p.pk) for p in posts]

    if request.is_ajax():
        return render(request, 'pin2/__search.html', {
            'results': results,
            'posts': ps,
            'query': query,
            'r': r,
            'offset': offset + row_per_page,
        })

    return render(request, 'pin2/result.html', {
        'results': results,
        'posts': ps,
        'query': query,
        'r': r,
        'offset': offset + row_per_page,
    })


def category_top(request, category_id):
    row_per_page = 20
    cat = get_object_or_404(Category, pk=category_id)
    results = []
    posts_list = []
    offset = int(request.GET.get('offset', 0))

    posts = SearchQuerySet().models(Post)\
        .filter(category_i=category_id)\
        .order_by('-cnt_like_i')[offset:offset + 1 * row_per_page]

    for post in posts:
        if not check_block(user_id=post.user.id, blocked_id=request.user.id):
            post_json = post_item_json(post_id=post.pk, cur_user_id=request.user.id)
            if post_json:
                posts_list.append(post_json)

    if request.is_ajax():
        return render(request, 'pin2/__search.html', {
            'results': results,
            'posts': posts_list,
            'offset': offset + row_per_page,
        })

    return render(request, 'pin2/category_top.html', {
        'results': results,
        'posts': posts_list,
        'offset': offset + row_per_page,
        'cur_cat': cat
    })


def tags(request, tag_name):
    return HttpResponseRedirect(reverse('hashtags', args=[tag_name]))
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
    posts_list = []
    query = tag_name
    related_tags = []
    total_count = 0
    tags = ['کربلا']

    if query in [u'عروس', u'عاشقانه'] and not request.user.is_authenticated():
        return render(request, 'pin2/samandehi.html')

    offset = int(request.GET.get('offset', 0))

    post_queryset = SearchQuerySet().models(Post)\
        .filter(tags=tag_name).facet('tags', mincount=1)

    ''' select posts'''
    posts = post_queryset\
        .order_by('-timestamp_i')[offset:offset + row_per_page]

    for post in posts:
        # if not check_block(user_id=post.user.id, blocked_id=request.user.id):
        post_json = post_item_json(post_id=post.pk,
                                   cur_user_id=request.user.id)
        if post_json:
            posts_list.append(post_json)

    ''' related tags query '''
    tags_facet = post_queryset.facet_counts()

    result = tags_facet['fields']['tags']

    if not result:
        result = []

    for key, val in result[:10]:
        if key != tag_name:
            related_tags.append(key)
        else:
            total_count = val

    if not query:
        return render(request, 'pin2/tags.html', {
            'tags': tags,
            'total_count': total_count
        })

    if request.is_ajax():
        return render(request, 'pin2/__search.html', {
            'posts': posts_list,
            'query': query,
            'offset': offset + row_per_page,
            'total_count': total_count,
            'related_tags': related_tags
        })

    return render(request, 'pin2/tag.html', {
        'posts': posts_list,
        'query': query,
        'page_title': tag_name,
        'offset': offset + row_per_page,
        'total_count': total_count,
        'related_tags': related_tags
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
    user = get_object_or_404(User, username=user_namefg)
    user_id = int(user.id)
    profile, created = Profile.objects.get_or_create(user_id=user_id)
    older = request.POST.get('older', False)
    following = None

    if not check_block(user_id=user.id, blocked_id=request.user.id):

        if older:
            following = Follow.objects\
                .filter(follower_id=user_id, id__lt=older).order_by('-id')[:16]
        else:
            following = Follow.objects.filter(follower_id=user_id)\
                .order_by('-id')[:16]

    if request.is_ajax():
        if following and following.exists():
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
    friends = None

    if not check_block(user_id=user.id, blocked_id=request.user.id):
        if older:
            friends = Follow.objects.filter(following_id=user_id, id__lt=older)\
                .order_by('-id')[:16]
        else:
            friends = Follow.objects.filter(following_id=user_id)\
                .order_by('-id')[:16]
    if request.is_ajax():
        if friends and friends.exists():
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
    return HttpResponseRedirect(reverse('pin-absuser-like',
                                        args=[user.username]))
    profile = Profile.objects.get(user_id=user_id)

    pid = get_request_pid(request)
    pl = Likes.user_likes(user_id=user_id, pid=pid)
    arp = []

    for pll in pl:
        try:
            arp.append(post_item_json(post_id=pll, cur_user_id=request.user.id))
        except:
            pass

    latest_items = arp

    if request.is_ajax():
        if latest_items:
            return render(request, 'pin2/_items_2.html', {
                'latest_items': latest_items
            })
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin2/user__likes.html', {
            'latest_items': latest_items,
            'user_id': user_id,
            'page': "profile",
            'profile': profile,
            'cur_user': user
        })


def absuser_like(request, user_namel):
    try:
        user = AuthCache.user_from_name(username=user_namel)
    except User.DoesNotExist:
        raise Http404

    status = True
    user_id = user.id

    profile, created = Profile.objects.get_or_create(user_id=user_id)
    if profile.banned:
        return render(request, 'pin2/samandehi.html')

    if request.user.is_authenticated():
        if check_block(user_id=user.id, blocked_id=request.user.id):
            status = False

    pid = get_request_pid(request)
    pl = Likes.user_likes(user_id=user_id, pid=pid)
    arp = []

    r_user_id = request.user.id
    if status:
        for pll in pl:
            ob = post_item_json(post_id=int(pll), cur_user_id=r_user_id)
            if ob:
                arp.append(ob)

    latest_items = arp

    if request.is_ajax():
        if latest_items:
            return render(request, 'pin2/_items_2_v6.html', {
                'latest_items': latest_items
            })
        else:
            return HttpResponse(0)

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
        'page': 'profile'
    })


def latest(request):
    pid = get_request_pid(request)

    pl = Post.latest(pid=pid)
    arp = []
    last_id = None
    next_url = None

    if request.user.id:
        viewer_id = str(request.user.id)
    else:
        viewer_id = str(get_user_ip(request, to_int=True))

    ad = Ads.get_ad(user_id=viewer_id)
    if ad:
        try:
            if ad.post not in pl:
                pl.append(str(ad.post.id))
        except:
            pass

    for pll in pl:
        pll_id = int(pll)
        ob = post_item_json(post_id=pll_id, cur_user_id=request.user.id)
        if ob:
            if not check_block(user_id=ob['user']['id'], blocked_id=request.user.id):
                arp.append(ob)
        last_id = pll

    if arp and last_id:
        next_url = reverse('pin-latest') + "?pid=" + last_id

    if request.is_ajax():
        if arp:
            return render(request, 'pin2/_items_2_v6.html', {
                'latest_items': arp,
                'next_url': next_url,
            })
        else:
            return HttpResponse(0)

    return render(request, 'pin2/latest_redis.html', {
        'latest_items': arp,
        'page': 'latest',
        'next_url': next_url,
    })


def category(request, cat_id):
    cat = get_object_or_404(Category, pk=cat_id)

    cat_id = cat.id
    pid = get_request_pid(request)
    pl = Post.latest(pid=pid, cat_id=cat_id)
    arp = []

    for pll in pl:
        pll_id = int(pll)
        ob = post_item_json(post_id=pll_id, cur_user_id=request.user.id)
        if ob:
            if not check_block(user_id=ob['user']['id'], blocked_id=request.user.id):
                arp.append(ob)

    latest_items = arp

    if request.is_ajax():
        if latest_items:
            return render(request, 'pin2/_items_2_v6.html', {
                'latest_items': latest_items
            })
        else:
            return HttpResponse(0)

    return render(request, 'pin2/category_redis.html', {
        'latest_items': latest_items,
        'cur_cat': cat, 'page': 'category'
    })


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
    ps = []
    for post in posts:
        # if not check_block(user_id=post.user.id, blocked_id=request.user.id):
        post_json = post_item_json(post_id=post.pk)
        if post_json:
            ps.append(post_item_json(post_id=post.pk))

    if request.is_ajax():
        return render(request, 'pin2/__search.html', {
            'posts': ps,
            'offset': offset + 20
        })

    return render(request, 'pin2/popular.html', {
        'posts': ps,
        'offset': offset + 20
    })


def topuser(request):
    top_user = Profile.objects.all().order_by('-score')[:48]
    for tu in top_user:
        tu.follow_status = Follow.objects\
            .filter(follower=request.user.id, following=tu.user_id).count()

    return render(request, 'pin2/topuser.html', {'top_user': top_user})


def topgroupuser(request):
    cats = Category.objects.all()
    for cat in cats:
        cat.tops = []
        leaders = LikesRedis().get_leaderboards_groups(category=cat.id)
        for leader in leaders:
            o = {}
            user_id = int(leader[0])
            user_score = leader[1]
            o['sum_like'] = int(user_score)
            u = User.objects.get(id=user_id)
            o['user'] = u
            cat.tops.append(o)

    return render(request, 'pin2/topgroupuser.html', {'cats': cats})


def user(request, user_id, user_name=None):
    user = get_object_or_404(User, pk=user_id)
    return HttpResponseRedirect(reverse('pin-absuser', args=[user.username]))


def absuser(request, user_name=None):
    try:
        user = AuthCache.user_from_name(username=user_name)
    except User.DoesNotExist:
        raise Http404

    user_id = user.id

    try:
        profile = Profile.objects.get(user_id=user_id)
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user_id=user_id)

    if profile.banned and not request.user.is_authenticated():
        return render(request, 'pin2/samandehi.html')

    ban_by_admin = False
    if request.user.is_superuser and not user.is_active:
        from pin.models import Log
        ban_by_admin = Log.objects.filter(object_id=user_id,
                                          content_type=Log.USER).order_by('-id')
        if ban_by_admin:
            ban_by_admin = ban_by_admin[0].text

    timestamp = get_request_timestamp(request)
    if timestamp == 0:
        lt = Post.objects.only('id').filter(user=user_id)\
            .order_by('-timestamp')[:20]
    else:
        lt = Post.objects.only('id').filter(user=user_id)\
            .extra(where=['timestamp<%s'], params=[timestamp])\
            .order_by('-timestamp')[:20]

    # profile.cnt_follower = Follow.objects.filter(following_id=user.id).count()
    # profile.cnt_following = Follow.objects.filter(follower_id=user.id).count()

    latest_items = []
    if not check_block(user_id=profile.user.id, blocked_id=request.user.id):
        for li in lt:
            pob = post_item_json(li.id, cur_user_id=request.user.id)
            if pob:
                latest_items.append(pob)

    if request.is_ajax():
        if latest_items:
            return render(request, 'pin2/_items_2_v6.html', {
                'latest_items': latest_items,
                'ptime': True,
            })
        else:
            return HttpResponse(0)

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
        'ptime': True,
        'follow_status': follow_status,
        'following_status': following_status,
        'ban_by_admin': ban_by_admin,
        'user_id': int(user_id),
        'profile': profile,
        'page': "profile",
    })


def item(request, item_id):
    MonthlyStats.log_hit(object_type=MonthlyStats.VIEW)

    try:
        # post = Post.objects.get(id=item_id)
        post = post_item_json(post_id=item_id)
        if not post:
            raise Post.DoesNotExist
    except Post.DoesNotExist:
        raise Http404("Post does not exist")

    # if int(item_id) == 14470480:
    #     from models_redis import PostView
    #     PostView(14470480).inc_view_test()

    # mlts = []

    # post["mlt"] = mlts

    if request.user.is_authenticated():
        if post and check_block(user_id=post["user"]["id"], blocked_id=request.user.id):
            return HttpResponseRedirect('/')

    # post["tag"] = []

    # post["likes"] = LikesRedis(post_id=post["id"])\
    #     .get_likes(offset=0, limit=5, as_user_object=True)

    follow_status = 0
    if request.user.is_authenticated():
        follow_status = Follow.objects.filter(follower=request.user.id,
                                              following=post["user"]["id"]).count()

    comments_url = reverse('pin-get-comments', args=[post["id"]])
    related_url = reverse('pin-item-related', args=[post["id"]])

    # try:
    #     permission = UserPermissions.objects.get(user=request.user)
    # except Exception, e:
    #     print str(e), "function post_item permission"

    if request.is_ajax():
        return render(request, 'pin2/items_inner.html', {
            'post': post, 'follow_status': follow_status
        })

    return render(request, 'pin2/item.html', {
        'post': post,
        'follow_status': follow_status,
        'comments_url': comments_url,
        'page': 'item',
        'related_url': related_url,
        # 'comment_status': permission.comment
    }, content_type="text/html")


def post_likers(request, post_id, offset=0):
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
    offset = int(request.GET.get('offset', 0))

    try:
        post = Post.objects.get(id=item_id)
    except Post.DoesNotExist:
        raise Http404

    cache_str = Post.MLT_CACHE_STR.format(item_id, offset)
    mltis = cache.get(cache_str)
    if not mltis:
        mlt = SearchQuerySet().models(Post)\
            .more_like_this(post)[offset:offset + Post.GLOBAL_LIMIT]

        mltis = [int(pmlt.pk) for pmlt in mlt]
        cache.set(cache_str, mltis, Post.MLT_CACHE_TTL)

    related_posts = []
    for pmlt in mltis:
        ob = post_item_json(post_id=pmlt, cur_user_id=request.user.id)
        if ob:
            related_posts.append(ob)

    ''' age related_posts khali bud az category miyarim'''
    if not related_posts:
        post_ids = Post.latest(cat_id=post.category_id)
        for post_id in post_ids:
            if post.id != post_id:
                post_json = post_item_json(post_id=int(post_id), cur_user_id=request.user.id)
                related_posts.append(post_json)

    post.mlt = related_posts

    if request.is_ajax():
        return render(request, 'pin2/_items_related.html', {
            'post': post
        })

    return render(request, 'pin2/item_related.html', {
        'post': post,
    }, content_type="text/html")


def get_comments(request, post_id):
    offset = int(request.GET.get('offset', 0))
    comments = Comments.objects.filter(object_pk=post_id)\
        .order_by('-id')\
        .only('id', 'user__username', 'user__id', 'comment', 'submit_date')[offset:offset + 1 * 10]

    if len(comments) == 0:
        return HttpResponse(0)

    return render(request, 'pin2/__comments_box.html', {
        'comments': comments
    })


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


def email_register(request):
    return render(request, 'pin2/emails/on_register.html', {
        'page': 'feedback'
    })


def pass_reset(request):
    return render(request, 'pin2/emails/on_reset_pass.html', {
        'page': 'feedback'
    })


def newsletter(request):
    posts_list = []
    posts = Post.objects.filter(user_id=21).order_by('-id')
    for post in posts:
        post_item = post_item_json(post_id=post.id, cur_user_id=request.user.id)
        posts_list.append(post_item)
    return render(request, 'pin2/emails/newsletter.html', {
        'posts': posts_list,
        'page': 'newsletter'
    })
