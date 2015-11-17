# coding: utf-8
from io import FileIO, BufferedWriter
import time

from django.conf import settings
from django.core.cache import cache
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import F, Sum
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, HttpResponseForbidden,\
    HttpResponseBadRequest, HttpResponseNotFound

from tastypie.models import ApiKey

from pin.models import Post, Comments, Comments_score,\
    Follow, Stream, Report

from pin.forms import PinDirectForm, PinDeviceUpdate
from pin.tools import create_filename, AuthCache, check_block,\
    log_act, post_after_delete, get_user_ip, get_post_user_cache
from pin.context_processors import is_police

MEDIA_ROOT = settings.MEDIA_ROOT


def check_auth(request):
    token = request.GET.get('token', '')
    if not token:
        return False

    try:
        # api = ApiKey.objects.get(key=token)
        # user = api.user
        user = AuthCache.user_from_token(token)
        if not user:
            return False
        user._ip = get_user_ip(request)

        if not user.is_active:
            return False
        else:
            return user
    except ApiKey.DoesNotExist:
        return False

    return False


@csrf_exempt
def like(request):
    log_act("wisgoon.api.post.liking.count")
    user = check_auth(request)

    if not user:
        return HttpResponseForbidden('error in user validation',
                                     content_type="application/json")

    if request.method != "POST":
        return HttpResponseBadRequest('error in parameters',
                                      content_type="application/json")

    post_id = int(request.POST.get('post_id', None))
    if not post_id:
        return HttpResponseBadRequest('erro in post id',
                                      content_type="application/json")
    try:
        post = get_post_user_cache(post_id=post_id)
        # post = Post.objects.only('user').get(pk=post_id)
    except Post.DoesNotExist:
        return HttpResponse('0', content_type="application/json")

    from models_redis import LikesRedis
    like, dislike, current_like = LikesRedis(post_id=post_id)\
        .like_or_dislike(user_id=user.id, post_owner=post.user_id)

    if like:
        return HttpResponse('+1', content_type="application/json")
    else:
        return HttpResponse('-1', content_type="application/json")

    return HttpResponse('0', content_type="application/json")


@csrf_exempt
def post_comment(request):
    log_act("wisgoon.api.post.commenting.count")
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden('error in user validation',
                                     content_type="application/json")

    data = request.POST.copy()
    comment = data.get('comment')
    object_pk = data.get("object_pk")
    if not data or not comment or not object_pk:
        return HttpResponse(0, content_type="application/json")

    if user.profile.score < settings.SCORE_FOR_COMMENING:
        return HttpResponse(u"امتباز شما باید بالای 5000 باشد.",
                            content_type="application/json")

    try:
        post = get_post_user_cache(post_id=object_pk)
        # post = Post.objects.only('user').get(id=object_pk)
        if check_block(user_id=post.user_id, blocked_id=user.id):
            if not is_police(request, flat=True):
                return HttpResponse(0)

        Comments.objects.create(object_pk_id=object_pk,
                                comment=comment,
                                user_id=user.id,
                                ip_address=user._ip)
        return HttpResponse(1, content_type="application/json")
    except Exception, e:
        return HttpResponse(0, content_type="application/json")


@csrf_exempt
def post_report(request):
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden('error in user validation')

    post_id = request.POST.get('post_id', None)
    if not post_id:
        return HttpResponseForbidden('error in params')

    if post_id and Post.objects.filter(pk=post_id).exists():
        r, created = Report.objects.get_or_create(user_id=user.id, post_id=post_id)
        if created:
            Post.objects.filter(pk=post_id).update(report=F('report') + 1)

        return HttpResponse(1)
    else:
        return HttpResponseNotFound('post not found')

    return HttpResponseBadRequest(0)


@csrf_exempt
def comment_report(request, comment_id):
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden('error in user validation')

    if comment_id and Comments.objects.filter(pk=comment_id).exists():
        Comments.objects.filter(pk=comment_id).update(reported=True)
        return HttpResponse(1)
    else:
        return HttpResponseNotFound('post not found')

    return HttpResponseBadRequest(0)


@csrf_exempt
def comment_score(request, comment_id, score):
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden('error in user validation')

    score = int(score)
    scores = [1, 0]
    if score not in scores:
        return HttpResponseBadRequest('error in scores')

    if score == 0:
        score = -1

    try:
        comment = Comments.objects.get(pk=comment_id)
        comment_score, created = Comments_score.objects\
            .get_or_create(user=user, comment=comment)
        if score != comment_score.score:
            comment_score.score = score
            comment_score.save()

        sum_score = Comments_score.objects\
            .filter(comment=comment).aggregate(Sum('score'))
        comment.score = sum_score['score__sum']
        comment.save()
        return HttpResponse(sum_score['score__sum'])

    except Comments.DoesNotExist:
        return HttpResponseNotFound('comment not found')

    return HttpResponseBadRequest('error')


@csrf_exempt
def post_delete(request, item_id):
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden('error in user validation')

    try:
        post = get_post_user_cache(post_id=item_id)
        if post.user_id == user.id:
            post_after_delete(post=post, user=user,
                              ip_address=get_user_ip(request))
            post.delete()
            return HttpResponse('1')
    except Post.DoesNotExist:
        return HttpResponseNotFound('post not exists or not yours')

    return HttpResponseBadRequest('bad request')


@csrf_exempt
def post_update(request, item_id):
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden('error in user validation')

    try:
        post = Post.objects.get(pk=int(item_id), user=user)
    except Post.DoesNotExist:
        return HttpResponseNotFound('post not found or not yours')

    if request.method == 'POST':
        form = PinDeviceUpdate(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return HttpResponse('success')
        else:
            return HttpResponseBadRequest('error in form')

    return HttpResponseBadRequest('bad request')


def follow(request, following, action):
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden('error in user validation')

    if int(following) == user.id:
        return HttpResponseForbidden('not need following himself')

    try:
        following = User.objects.get(pk=int(following))
        try:
            follow, created = Follow.objects\
                .get_or_create(follower=user, following=following)
        except MultipleObjectsReturned:
            Follow.objects.filter(follower=user, following=following).delete()
            follow, created = Follow.objects\
                .get_or_create(follower=user, following=following)

        if int(action) == 0 and follow:
            follow.delete()
            Stream.objects.filter(following=following, user=user)\
                .all().delete()
        # elif created:
            # posts = Post.objects.only('timestamp').filter(user=following)\
            #     .order_by('-timestamp')[:100]

            # for post in posts:
            #     s, created = Stream.objects\
            #         .get_or_create(post=post,
            #                        user=user,
            #                        date=post.timestamp,
            #                        following=following)

    except User.DoesNotExist:
        return HttpResponse('User does not exists')

    return HttpResponse('1')


@csrf_exempt
def post_send(request):
    debug_str = "********************"
    start_time = str(time.time())
    debug_str += "\n " + str(start_time)
    debug_str += "\n step 1 " + str(time.time())
    user = check_auth(request)
    debug_str += "\n step 2 " + str(time.time())
    if not user:
        print 'error in user validation'
        return HttpResponseForbidden('error in user validation')
    debug_str += "\n step 3 " + str(time.time())

    if request.method != 'POST':
        print "not post"
        return HttpResponseBadRequest('bad request post')
    debug_str += "\n step 4 " + str(time.time())

    try:
        form = PinDirectForm(request.POST, request.FILES)
    except IOError:
        print "ioerror"
        return HttpResponseBadRequest('bad request')

    debug_str += "\n step 5 " + str(time.time())

    if form.is_valid():
        debug_str += "\n step 6 " + str(time.time())
        upload = request.FILES.values()[0]
        filename = create_filename(upload.name)
        debug_str += "\n step 7 " + str(time.time())
        try:
            u = "%s/pin/%s/images/o/%s" % (MEDIA_ROOT, settings.INSTANCE_NAME, filename)
            with BufferedWriter(FileIO(u, "wb")) as dest:
                for c in upload.chunks():
                    dest.write(c)

            debug_str += "\n step 8 " + str(time.time())

            model = Post()
            model.image = "pin/%s/images/o/%s" % (settings.INSTANCE_NAME, filename)
            model.user = user
            model.timestamp = time.time()
            model.text = form.cleaned_data['description']
            model.category_id = form.cleaned_data['category']
            model.device = 2
            model.save()
            debug_str += "\n step 9 " + str(time.time())
            debug_str += "\n\n" + start_time
            print debug_str

            return HttpResponse('success')
        except IOError, e:
            print str(e), MEDIA_ROOT
            print "294"
            return HttpResponseBadRequest('error')

        print "297"
        return HttpResponseBadRequest('bad request in form')
    else:
        print form.errors
        print 301
        HttpResponseBadRequest('error in form validation')

    print "305"
    return HttpResponseBadRequest('bad request')
