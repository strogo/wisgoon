# coding: utf-8
from io import FileIO, BufferedWriter
import time

from django.conf import settings
from django.core.exceptions import MultipleObjectsReturned
from django.db.models import Sum
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponse, HttpResponseForbidden,\
    HttpResponseBadRequest, HttpResponseNotFound, UnreadablePostError

from tastypie.models import ApiKey

from pin.forms import PinDirectForm, PinDeviceUpdate
from pin.models import Post, Comments, Comments_score,\
    Follow, ReportedPost
from pin.tools import create_filename, AuthCache, check_block,\
    post_after_delete, get_user_ip, get_post_user_cache, fix_rotation

MEDIA_ROOT = settings.MEDIA_ROOT


def check_auth(request):
    token = request.GET.get('token', '')
    if not token:
        return False

    try:
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
    return HttpResponse('+1', content_type="application/json")
    user = check_auth(request)

    if not user:
        return HttpResponseForbidden(_('error in user validation'),
                                     content_type="application/json")

    if request.method != "POST":
        return HttpResponseBadRequest(_('error in entered parameters'),
                                      content_type="application/json")
    try:
        post_id = int(request.POST.get('post_id', None))
    except UnreadablePostError:
        return HttpResponseBadRequest(_('There is no post id'),
                                      content_type="application/json")
    if not post_id:
        return HttpResponseBadRequest(_('There is no post id'),
                                      content_type="application/json")
    try:
        post = get_post_user_cache(post_id=post_id)
    except Post.DoesNotExist:
        return HttpResponse('0', content_type="application/json")

    from models_redis import LikesRedis
    like, dislike, current_like = LikesRedis(post_id=post_id)\
        .like_or_dislike(user_id=user.id,
                         post_owner=post.user_id,
                         user_ip=user._ip,
                         category=post.category_id)

    if like:
        return HttpResponse('+1', content_type="application/json")
    else:
        return HttpResponse('-1', content_type="application/json")

    return HttpResponse('0', content_type="application/json")


@csrf_exempt
def post_comment(request):
    # user = check_auth(request)
    return HttpResponse(0, content_type="application/json")
    user = None
    if not user:
        return HttpResponseForbidden(_('error in user validation'),
                                     content_type="application/json")
    try:
        data = request.POST.copy()
    except UnreadablePostError:
        return HttpResponse(0, content_type="application/json")

    comment = data.get('comment')
    object_pk = data.get("object_pk")
    if not data or not comment or not object_pk:
        return HttpResponse(0, content_type="application/json")

    if user.profile.score < settings.SCORE_FOR_COMMENING:
        return HttpResponse(_("You should be rated above 5000"),
                            content_type="application/json")

    try:
        post = get_post_user_cache(post_id=object_pk)
        if check_block(user_id=post.user_id, blocked_id=user.id):
            return HttpResponse(0)

        Comments.objects.create(object_pk_id=object_pk,
                                comment=comment,
                                user_id=user.id,
                                ip_address=user._ip)
        return HttpResponse(1, content_type="application/json")
    except Exception:
        return HttpResponse(0, content_type="application/json")


@csrf_exempt
def post_report(request):
    return HttpResponseBadRequest(0)
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden(_('error in user validation'))

    post_id = request.POST.get('post_id', None)
    if not post_id:
        return HttpResponseForbidden(_('error in entered params'))

    if post_id and Post.objects.filter(pk=post_id).exists():
        ReportedPost.post_report(post_id=post_id, reporter_id=user.id)

        return HttpResponse(1)
    else:
        return HttpResponseNotFound(_('post not found'))

    return HttpResponseBadRequest(0)


@csrf_exempt
def comment_report(request, comment_id):
    return HttpResponseBadRequest(0)
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden(_('error in user validation'))

    if comment_id and Comments.objects.filter(pk=comment_id).exists():
        Comments.objects.filter(pk=comment_id).update(reported=True)
        return HttpResponse(1)
    else:
        return HttpResponseNotFound(_('post not found'))

    return HttpResponseBadRequest(0)


@csrf_exempt
def comment_score(request, comment_id, score):
    return HttpResponseBadRequest('error in scores')
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden(_('error in user validation'))

    score = int(score)
    scores = [1, 0]
    if score not in scores:
        return HttpResponseBadRequest(_('There is no score'))

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
        return HttpResponseNotFound(_('comment not found'))

    return HttpResponseBadRequest('error in scores')


@csrf_exempt
def post_delete(request, item_id):
    return HttpResponse('1')
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden(_('error in user validation'))

    try:
        post = get_post_user_cache(post_id=item_id)
        if post.user_id == user.id:
            post_after_delete(post=post, user=user,
                              ip_address=get_user_ip(request))
            post.delete()
            return HttpResponse('1')
    except Post.DoesNotExist:
        return HttpResponseNotFound(_('post not exists or not yours'))

    return HttpResponseBadRequest(_('bad request'))


@csrf_exempt
def post_update(request, item_id):
    return HttpResponse(_('successfully updated post'))
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden(_('error in user validation'))

    try:
        post = Post.objects.get(pk=int(item_id), user=user)
    except Post.DoesNotExist:
        return HttpResponseNotFound(_('post not found or post not yours'))

    if request.method == 'POST':
        form = PinDeviceUpdate(request.POST, instance=post)
        if form.is_valid():
            form._user_ip = get_user_ip(request)
            form.save()
            return HttpResponse(_('successfully updated post'))
        else:
            return HttpResponseBadRequest(_('error in update post form'))

    return HttpResponseBadRequest(_('bad request'))


def follow(request, following, action):
    return HttpResponse('1')
    user = check_auth(request)
    if not user:
        return HttpResponseForbidden(_('error in user validation'))

    if int(following) == user.id:
        return HttpResponseForbidden(_('not need following himself'))

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
    except User.DoesNotExist:
        return HttpResponse(_('User does not exist'))

    return HttpResponse('1')


@csrf_exempt
def post_send(request):
    return HttpResponseBadRequest('bad request')
    user = check_auth(request)

    if not user:
        return HttpResponseForbidden(_('error in user validation'))

    if request.method != 'POST':
        return HttpResponseBadRequest(_('bad request post'))

    try:
        form = PinDirectForm(request.POST, request.FILES)
    except IOError:
        print "ioerror"
        return HttpResponseBadRequest(_('bad request'))

    if form.is_valid():
        upload = request.FILES.values()[0]
        filename = create_filename(upload.name)
        try:
            u = "{}/pin/{}/images/o/{}".\
                format(MEDIA_ROOT, settings.INSTANCE_NAME, filename)
            with BufferedWriter(FileIO(u, "wb")) as dest:
                for c in upload.chunks():
                    dest.write(c)

            # image rotate
            fix_rotation(u)

            model = Post()
            model.image = "pin/{}/images/o/{}".\
                format(settings.INSTANCE_NAME, filename)
            model.user = user
            model.timestamp = time.time()
            model.text = form.cleaned_data['description']
            model.category_id = form.cleaned_data['category']
            model.device = 2
            model._user_ip = get_user_ip(request)
            model.save()
            return HttpResponse('success')

            return HttpResponse(_('successfully upload post'))
        except IOError, e:
            print str(e), MEDIA_ROOT
            return HttpResponseBadRequest('error')
            return HttpResponseBadRequest(_('error'))

        return HttpResponseBadRequest('bad request in form')
        return HttpResponseBadRequest(_('bad request in form'))
    else:
        print form.errors
        HttpResponseBadRequest('error in form validation')
        HttpResponseBadRequest(_('error in form validation'))

    return HttpResponseBadRequest('bad request')
    return HttpResponseBadRequest(_('bad request'))
