# -*- coding: utf-8 -*-
import time
from datetime import datetime
from datetime import timedelta
from haystack.query import SearchQuerySet

from django.conf import settings
from django.db.models import Q
from django.core.cache import cache
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from pin.api6.http import return_json_data, return_bad_request,\
    return_not_found, return_un_auth
from pin.api6.tools import get_next_url, get_int, save_post,\
    get_list_post, get_objects_list, ad_item_json, post_item_json
from pin.models import Post, Report, Ad, Block, ReportedPost
from pin.tools import AuthCache, get_post_user_cache, get_user_ip,\
    post_after_delete


GLOBAL_LIMIT = 10


def latest(request):
    cur_user = None
    last_item = None
    hot_post = None
    data = {
        'meta': {
            'limit': GLOBAL_LIMIT,
            'next': '',
            'total_count': 1000
        }
    }

    before = request.GET.get('before', None)
    token = request.GET.get('token', '')

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if not before:
        before = 0

    pl = Post.latest(pid=before, limit=GLOBAL_LIMIT)
    posts = get_list_post(pl, from_model=settings.STREAM_LATEST)

    if cur_user:
        viewer_id = str(cur_user)
    else:
        viewer_id = str(get_user_ip(request, to_int=True))

    ad = Ad.get_ad(user_id=viewer_id)
    if ad:
        hot_post = int(ad.post_id)
    if hot_post:
        posts = list([hot_post]) + list(posts)

    data['objects'] = get_objects_list(posts,
                                       cur_user_id=cur_user,
                                       r=request)

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-post-latest',
                                            token=token,
                                            before=last_item)

    return return_json_data(data)


def friends(request):
    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    before = request.GET.get('before', None)
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)
    else:
        return return_bad_request()

    if not cur_user:
        return return_bad_request()

    if before:
        idis = Post.user_stream_latest(user_id=cur_user, pid=before)
    else:
        idis = Post.user_stream_latest(user_id=cur_user)

    posts = get_list_post(idis, from_model=settings.STREAM_LATEST)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)
    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-post-friends',
                                            token=token, before=last_item)

    return return_json_data(data)


def category(request, category_id):
    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    before = request.GET.get('before', None)
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if not before:
        before = 0

    pl = Post.latest(pid=before, cat_id=category_id)
    from_model = "%s_%s" % (settings.STREAM_LATEST_CAT, category_id)
    posts = get_list_post(pl, from_model=from_model)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)
    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-post-category',
                                            token=token, before=last_item,
                                            url_args={
                                                "category_id": category_id
                                            })

    return return_json_data(data)


def choices(request):
    cur_user = None
    data = {
        'meta': {
            'limit': GLOBAL_LIMIT,
            'next': "",
            'total_count': 1000
        }
    }

    before = request.GET.get('before', None)
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if not before:
        before = 0

    pl = Post.home_latest(pid=before, limit=GLOBAL_LIMIT)
    posts = get_list_post(pl)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)
    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-post-choices',
                                            token=token, before=last_item)

    return return_json_data(data)


def search(request):
    limit = 20
    query = request.GET.get('q', '')

    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    offset = int(request.GET.get('offset', 0))
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    posts = SearchQuerySet().models(Post)\
        .filter(content__contains=query)[offset:offset + limit]

    idis = []
    for pmlt in posts:
        idis.append(pmlt.pk)

    posts = Post.objects.values_list('id', flat=True).filter(id__in=idis)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)

    data['meta']['next'] = get_next_url(url_name='api-6-post-search',
                                        token=token, offset=offset + limit,
                                        q=query)

    return return_json_data(data)


def item(request, item_id):
    cur_user = None
    data = {}
    token = request.GET.get('token', None)

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    posts = get_list_post([item_id])

    try:
        data = get_objects_list(posts, cur_user_id=cur_user,
                                r=request)[0]
    except IndexError:
        return return_not_found()

    return return_json_data(data)


def report(request, item_id):
    token = request.GET.get('token', False)
    if token:
        current_user = AuthCache.id_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    try:
        post = Post.objects.get(id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    ReportedPost.post_report(post_id=post.id, reporter_id=current_user)

    try:
        Report.objects.get(user_id=current_user, post=post)
        created = False
    except Report.DoesNotExist:
        Report.objects.create(user_id=current_user, post=post)
        created = True

    if created:
        post.report = post.report + 1
        post.save()
        status = True
        msg = _('Successfully Add Report.')
    else:
        status = False
        msg = _('Your Report Already Exists.')

    data = {'status': status, 'msg': msg}
    return return_json_data(data)


@csrf_exempt
def edit(request, item_id):
    from pin.forms import PinUpdateForm

    # Get User From Token
    token = request.GET.get('token', False)
    if token:
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    # Get Post
    try:
        post = Post.objects.get(id=get_int(item_id))
    except Post.DoesNotExist:
        return return_not_found()

    # Check User and Update Post
    if current_user.is_superuser or post.user.id == current_user.id:

        form = PinUpdateForm(request.POST.copy(), instance=post)
        if form.is_valid():
            form.save()
        else:
            return return_json_data({'status': False, 'errors': form.errors})

        # Get Post Object
        try:
            posts = get_list_post([item_id])
            data = get_objects_list(posts, cur_user_id=current_user.id,
                                    r=request)[0]
        except IndexError:
            return return_not_found()
        return return_json_data({
            'status': True,
            'message': _('Successfully Updated'),
            'data': data
        })

    else:
        return return_json_data({
            'status': False,
            'message': _('Access Denied')
        })


@csrf_exempt
def send(request):
    # Get User From Token
    token = request.GET.get('token', False)
    if token:
        current_user = AuthCache.user_from_token(token=token)
        if not current_user:
            return return_un_auth()
    else:
        return return_bad_request()

    status, post, msg = save_post(request, current_user)
    if status is False:
        return return_json_data({'status': status, 'message': msg})

    try:
        posts = get_list_post([post.id])
        data = get_objects_list(posts, cur_user_id=current_user.id, r=request)[0]
    except IndexError:
        # print str(e), "function send_post permission"

        return return_json_data({
            'status': False,
            'message': _('Post Not Found')
        })

    if post.status == 1:
        msg = _('Your article has been sent.')
    elif post.status == 0:
        msg = _('Your article has been sent and displayed on the site after confirmation ')
    return return_json_data({'status': status, 'message': msg, 'post': data})


def user_post(request, user_id):
    before = int(request.GET.get('before', 0))
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    user_posts = Post.objects.values_list('id', flat=True)\
        .filter(user=user_id).order_by('-id')[before:before + 20]

    token = request.GET.get('token', False)
    current_user = None
    if token:
        current_user = AuthCache.id_from_token(token=token)

    if current_user:
        if Block.objects.filter(user_id=user_id, blocked_id=current_user).count():
            return return_not_found({
                'message': _('This User Has Blocked You')
            })

    data['objects'] = get_objects_list(user_posts, current_user)

    last_item = before + 20
    data['meta']['next'] = get_next_url(url_name='api-6-post-user',
                                        before=last_item,
                                        token=token,
                                        url_args={"user_id": user_id}
                                        )
    return return_json_data(data)


def related_post(request, item_id):
    data = {
        'meta': {
            'limit': GLOBAL_LIMIT,
            'next': "",
            'total_count': 1000
        },
        'objects': [],
    }

    token = request.GET.get('token', False)
    offset = int(request.GET.get('offset', 0))

    if offset > 100:
        return return_json_data(data)

    current_user = None
    if token:
        current_user = AuthCache.user_from_token(token=token)

    cache_str = Post.MLT_CACHE_STR.format(item_id, offset)
    mltis = cache.get(cache_str)
    if not mltis:
        try:
            post = Post.objects.get(id=int(item_id))
        except Exception, e:
            return return_not_found()

        mlt = SearchQuerySet().models(Post)\
            .more_like_this(post)[offset:offset + Post.GLOBAL_LIMIT]

        idis = [int(pmlt.pk) for pmlt in mlt]
        mltis = get_list_post(idis)
        cache.set(cache_str, mltis, Post.MLT_CACHE_TTL)

        if not mltis:
            post_ids = Post.latest(cat_id=post.category_id)
            for post_id in post_ids:
                if post.id != post_id:
                    post_json = post_item_json(post_id=int(post_id), cur_user_id=request.user.id)
                    mltis.append(post_json)

    data['objects'] = get_objects_list(mltis, current_user)
    data['meta']['next'] = get_next_url(url_name='api-6-post-related',
                                        token=token,
                                        offset=offset + Post.GLOBAL_LIMIT,
                                        url_args={
                                            "item_id": item_id}
                                        )
    return return_json_data(data)


def promoted(request):
    data = {}
    objects = []
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    before = get_int(request.GET.get('before', 0))
    token = request.GET.get('token', '')

    if token:
        user = AuthCache.user_from_token(token=token)
        if not user:
            return return_un_auth()
    else:
        return return_bad_request()

    ads = Ad.objects.filter(Q(owner=user) | Q(user=user))\
        .order_by("-id")[before:before + 20]

    for ad in ads:
        ad_json = ad_item_json(ad)
        objects.append(ad_json)

    data['objects'] = objects

    last_item = before + 20
    data['meta']['next'] = get_next_url(url_name='api-6-post-promoted',
                                        before=last_item,
                                        token=token
                                        )
    return return_json_data(data)


def hashtag(request, tag_name):
    token = request.GET.get('token', '')
    query = tag_name
    before = get_int(request.GET.get('before', 0))

    row_per_page = 20
    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': ''}

    if query:

        results = SearchQuerySet().models(Post).filter(tags=query)

        data['meta']['total_count'] = results.count()

        cur_user = AuthCache.id_from_token(token=token)
        posts = []
        for p in results.order_by('-timestamp_i')[before:before + row_per_page]:
            try:
                pp = int(p.object.id)
                posts.append(pp)
            except:
                pass

        data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                           r=request)

        data['meta']['next'] = get_next_url(url_name='api-6-post-hashtag',
                                            before=before + row_per_page,
                                            token=token,
                                            url_args={'tag_name': query}
                                            )
        return return_json_data(data)
    else:
        return return_bad_request()


@csrf_exempt
def delete(request, item_id):
    """Delete post."""
    # Get User From Token
    token = request.GET.get('token', False)
    if token:
        user = AuthCache.user_from_token(token=token)
        if not user:
            return return_un_auth()
    else:
        return return_bad_request(message=_("token error"))

    try:
        post = get_post_user_cache(post_id=item_id)
        if post.user_id == user.id:
            post_after_delete(post=post, user=user,
                              ip_address=get_user_ip(request))
            post.delete()
            return return_json_data({
                'status': True,
                'message': _('post deleted')
            })
    except Post.DoesNotExist:
        return return_json_data({
            'status': False,
            'message': _('post not exists or not yours')
        })

    return return_bad_request()


def promotion_prices(request):
    data = {
        "objects": [
            {
                "price": 500,
                "visitors": 1000
            },
            {
                "price": 1000,
                "visitors": 3000
            },
            {
                "price": 2000,
                "visitors": 6000,
            },
            {
                "price": 5000,
                "visitors": 15000
            }
        ]
    }
    return return_json_data(data)


@csrf_exempt
def post_promote(request, post_id):
    try:
        Post.objects.get(id=int(post_id))
    except Exception, Post.DoesNotExist:
        return return_not_found()

    user = None
    token = request.GET.get('token', '')

    if token:
        user = AuthCache.user_from_token(token=token)

    if not user or not token:
        return return_un_auth()

    profile = user.profile

    if request.method == "POST":
        mode = int(request.POST.get('mode', 0))
        if mode == 0:
            return return_bad_request()

        try:
            mode_price = Ad.TYPE_PRICES[mode]
        except KeyError:
            return return_json_data({"status": False,
                                     "message": u"عدد وارد شده اشتباه است."})

        if profile.credit >= int(mode_price):
            try:
                Ad.objects.get(post=int(post_id), ended=False)
                return return_json_data({"status": False,
                                         "message": u"این پست قبلا آگهی شده است"})
            except Exception, Ad.DoesNotExist:
                profile.dec_credit(amount=int(mode_price))
                Ad.objects.create(user_id=user.id,
                                  post_id=int(post_id),
                                  ads_type=mode,
                                  start=datetime.now(),
                                  ip_address=get_user_ip(request))
                return return_json_data({'status': True,
                                        'message': u'مطلب مورد نظر شما با موفقیت آگهی شد.'})

        else:
            return return_json_data({'status': False,
                                     'message': u'موجودی حساب شما برای آگهی دادن کافی نیست.'})

    return return_json_data({'status': False, 'message': 'error in data'})


def tops(request, period):
    cur_user = None
    periods = {
        'monthly': {
            'days': 30
        },
        'daily': {
            'days': 1
        },
        'weekly': {
            'days': 7
        },
        'new': {
            'hours': 8
        }
    }

    data = {
        'meta': {
            'limit': GLOBAL_LIMIT,
            'next': '',
            'total_count': 1000
        }
    }

    offset = int(request.GET.get('offset', 0))
    token = request.GET.get('token', '')

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if period in periods:
        dt_now = datetime.now().replace(minute=0, second=0, microsecond=0)

        date_from = dt_now - timedelta(**periods[period])

        if date_from:
            start_from = time.mktime(date_from.timetuple())
            pop_posts = SearchQuerySet().models(Post)\
                .filter(timestamp_i__gt=int(start_from))\
                .order_by('-cnt_like_i')[offset:offset + GLOBAL_LIMIT]

    else:
        pop_posts = SearchQuerySet().models(Post)\
            .order_by('-cnt_like_i')[offset:offset + GLOBAL_LIMIT]

    idis = [int(ps.pk) for ps in pop_posts]
    posts = get_list_post(idis)

    data['objects'] = get_objects_list(posts,
                                       cur_user_id=cur_user,
                                       r=request)

    data['meta']['next'] = get_next_url(url_name='api-6-post-tops',
                                        token=token,
                                        offset=offset + GLOBAL_LIMIT,
                                        url_args={
                                            "period": period
                                        })

    return return_json_data(data)
