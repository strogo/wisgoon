# -*- coding: utf-8 -*-
from pin.tools import AuthCache
from pin.models import Post, Report, Ad
from django.conf import settings
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from pin.api6.tools import get_next_url, get_int, save_post, get_list_post, get_objects_list
from pin.api6.http import return_json_data, return_bad_request, return_not_found, return_un_auth
from haystack.query import SearchQuerySet
from django.utils.translation import ugettext as _


def latest(request):
    cur_user = None
    last_item = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': '',
                    'total_count': 1000}

    before = request.GET.get('before', None)
    token = request.GET.get('token', '')

    if token:
        cur_user = AuthCache.id_from_token(token=token)

    if not before:
        before = 0

    pl = Post.latest(pid=before)
    posts = get_list_post(pl, from_model=settings.STREAM_LATEST)

    data['objects'] = get_objects_list(posts,
                                       cur_user_id=cur_user,
                                       r=request)

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-post-latest',
                                            token=token, before=last_item)

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

    pl = Post.home_latest(pid=before)
    posts = get_list_post(pl)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-post-choices',
                                            token=token, before=last_item)

    return return_json_data(data)


def search(request):
    row_per_page = 20
    query = request.GET.get('q', '')
    offset = int(request.GET.get('offset', 0))
    next_offset = offset + 1 * row_per_page

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

    posts = SearchQuerySet().models(Post)\
        .filter(content__contains=query)[offset:next_offset]

    idis = []
    for pmlt in posts:
        idis.append(pmlt.pk)

    posts = Post.objects.filter(id__in=idis).only(*Post.NEED_KEYS_WEB)

    data['objects'] = get_objects_list(posts, cur_user_id=cur_user,
                                       r=request)

    if data['objects']:
        data['meta']['next'] = get_next_url(url_name='api-6-post-search',
                                            token=token, offset=next_offset, q=query)

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
            data = get_objects_list(posts, cur_user_id=current_user.id, r=request)[0]
        except IndexError:
            return return_not_found()
        return return_json_data({'status': True, 'message': _('Successfully Updated'), 'data': data})

    else:
        return return_json_data({'status': False, 'message': _('Access Denied')})


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
        return return_json_data({'status': False, 'message': _('Post Not Found')})

    if post.status == 1:
        msg = _('مطلب شما با موفقیت ارسال شد.')
    elif post.status == 0:
        msg = _('مطلب شما با موفقیت ارسال شد و بعد از تایید در سایت نمایش داده می شود ')
    return return_json_data({'status': status, 'message': msg, 'post': data})


def user_post(request, user_id):
    before = request.GET.get('before', False)
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}
    if before:
        user_posts = Post.objects.only(*Post.NEED_KEYS_WEB)\
            .filter(user=user_id, id__lt=before).order_by('-id')[:20]
    else:
        user_posts = Post.objects.only(*Post.NEED_KEYS_WEB)\
            .filter(user=user_id).order_by('-id')[:20]

    data['objects'] = get_objects_list(user_posts, user_id)

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-post-user',
                                            before=last_item,
                                            url_args={"user_id": user_id}
                                            )
    return return_json_data(data)


def related_post(request, item_id):
    data = {}
    data['meta'] = {'limit': 10,
                    'next': "",
                    'total_count': 1000}

    token = request.GET.get('token', False)
    current_user = None
    if token:
        current_user = AuthCache.user_from_token(token=token)

    try:
        post = Post.objects.get(id=item_id)
    except Post.DoesNotExist:
        return return_not_found()

    mlt = SearchQuerySet().models(Post).more_like_this(post)[:10]

    idis = []
    for pmlt in mlt:
        idis.append(pmlt.pk)

    post.mlt = Post.objects.filter(id__in=idis).only(*Post.NEED_KEYS_WEB)

    data['objects'] = get_objects_list(post.mlt, current_user)
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

    if before:
        ads = Ad.objects.filter(Q(owner=user) | Q(user=user), id__lt=before).order_by("-id")[:20]
    else:
        ads = Ad.objects.filter(Q(owner=user) | Q(user=user)).order_by("-id")[:20]

    for ad in ads:
        o = {}
        o['post'] = get_objects_list([ad.post], cur_user_id=user.id, thumb_size=250)
        o['cnt_view'] = ad.get_cnt_view()
        o['user'] = ad.user.id
        o['ended'] = ad.ended
        o['owner'] = ad.owner.id
        # o['cnt_view'] = ad.cnt_view
        o['ads_type'] = ad.ads_type
        o['start'] = str(ad.start)
        o['end'] = str(ad.end)
        o['id'] = ad.id
        objects.append(o)

    data['objects'] = objects

    if data['objects']:
        last_item = data['objects'][-1]['id']
        data['meta']['next'] = get_next_url(url_name='api-6-post-user',
                                            before=last_item
                                            )
    return return_json_data(data)


def hashtag(request):
    token = request.GET.get('token', '')
    query = str(request.GET.get('q', ''))
    query = query.replace('#', '')
    before = get_int(request.GET.get('before', 0))

    row_per_page = 20
    cur_user = None
    data = {}
    data['meta'] = {'limit': 20,
                    'next': "",
                    'total_count': 1000}

    if query and token:

        results = SearchQuerySet().models(Post)\
            .filter(tags=query)\
            .order_by('-timestamp_i')[before:before + 1 * row_per_page]

        cur_user = AuthCache.id_from_token(token=token)
        posts = []
        for p in results:
            try:
                pp = Post.objects\
                    .only(*Post.NEED_KEYS2)\
                    .get(id=p.object.id)

                posts.append(pp)
            except:
                pass

        data['objects'] = get_objects_list(posts, cur_user_id=cur_user, r=request)

        if data['objects']:
            data['meta']['next'] = get_next_url(url_name='api-6-post-hashtag',
                                                before=20,
                                                token=token,
                                                q=query
                                                )
        return return_json_data(data)
    else:
        return return_bad_request()
