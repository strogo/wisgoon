# -*- coding: utf-8 -*-
from time import time
import re
import base64
import json
import datetime
import urllib
import requests
from shutil import copyfile

from django.db.models import Q
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseBadRequest, Http404, JsonResponse, UnreadablePostError


import pin_image
from pin.decorators import system_writable
from pin.api6.tools import post_item_json, notif_simple_json,\
    get_simple_user_object
from pin.crawler import get_images
from pin.forms import PinForm, PinUpdateForm
from user_profile.models import Profile
from pin.model_mongo import Notif
from pin.models_redis import ActivityRedis, NotificationRedis
from pin.notification_models import UserNotification, MyNotificationFeed
from pin.tasks import porn_feedback
from pin.models import Post, Follow, Ad, Block,\
    Report, Comments, Comments_score, Category, Bills2 as Bills, ReportedPost,\
    FollowRequest
from pin.tools import create_filename, get_user_ip, get_request_pid,\
    check_block, post_after_delete, check_user_state
from suds.client import Client
from tastypie.models import ApiKey


MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL
MERCHANT_ID = settings.MERCHANT_ID
SITE_URL = settings.SITE_URL


@login_required
def following(request):
    # pid = get_request_pid(request)
    # pl = Post.user_stream_latest(pid=pid, user_id=request.user.id)

    # arp = []
    # for pll in pl:
    #     pll_id = int(pll)
    #     ob = post_item_json(pll_id, cur_user_id=request.user.id)
    #     if ob:
    #         is_block = check_block(user_id=ob['user']['id'],
    #                                blocked_id=request.user.id)
    #         if not is_block:
    #             arp.append(ob)

    # latest_items = arp

    # sorted_objects = latest_items
    # cur_user = request.user
    # request_user_authenticated = request.user.is_authenticated()

    pid = get_request_pid(request)
    if settings.DEBUG:
        url = "http://127.0.0.1:8801/v7/post/friends/"
    else:
        url = "http://api.wisgoon.com/v7/post/friends/"
    payload = {}
    arp = []

    # Get request user token
    try:
        api_key = ApiKey.objects.only('key').get(user_id=request.user.id)
    except:
        api_key = None

    if api_key:
        token = api_key.key
        payload['token'] = token

    payload['before'] = pid

    # Get following post
    s = requests.Session()
    res = s.get(url, params=payload, headers={'Connection': 'close'})

    if res.status_code == 200:
        try:
            data = json.loads(res.content)
            arp = data['objects']
        except:
            pass

    if request.is_ajax():
        if arp:
            return render(request,
                          'pin2/_items_2_v6.html',
                          {'latest_items': arp})
        else:
            return HttpResponse(0)
    else:
        return render(request,
                      'pin2/following.html', {
                          'page': 'following',
                          'latest_items': arp
                      })


@login_required
@system_writable
def follow(request, following, action):
    message = ''
    is_follow = False
    pending = False
    current_user_id = request.user.id

    if int(following) == current_user_id:
        return HttpResponseRedirect(reverse('pin-home'))

    if check_block(user_id=int(following), blocked_id=current_user_id):
        return HttpResponseRedirect('/')

    try:
        following = User.objects.get(pk=int(following))
    except User.DoesNotExist:
        return HttpResponseRedirect('/')

    if int(action) == 1:
        if following.profile.is_private:
            FollowRequest.objects.get_or_create(user_id=current_user_id,
                                                target=following)
            message = _('Your follow request successfully send.')
            pending = True
        else:
            follow, created = Follow.objects\
                .get_or_create(follower_id=current_user_id,
                               following=following)
            message = _('Your connection successfully established.')
            is_follow = True
    else:
        try:
            follow = Follow.objects.get(follower_id=current_user_id,
                                        following=following)
            follow.delete()
            message = _('Your connection was successfully shut down')
        except Exception, e:
            message = _('Your connection was successfully shut down')
            print str(e)

    # try:
    #     follow, created = Follow.objects\
    #         .get_or_create(follower=request.user,
    #                        following=following)
    # except Exception, e:
    #     follow = Follow.objects.filter(follower=request.user,
    #                                    following=following)[0]
    #     created = False
    #     print str(e)

    # if int(action) == 0 and follow:
    #     follow.delete()
    #     Stream.objects.filter(following=following,
    #                           user=request.user).delete()
    #     message = _('Your connection was successfully shut down')
    #     is_follow = False
    # elif created:
    #     message = _('Your connection successfully established.')
    #     is_follow = True

    if request.is_ajax():
        data = {
            'status': True,
            'is_follow': is_follow,
            'message': message,
            'pending': pending,
            'count': following.profile.cnt_followers
        }
        return HttpResponse(json.dumps(data),
                            content_type='application/json')
    return HttpResponseRedirect(reverse('pin-user', args=[following.id]))


@login_required
@system_writable
def like(request, item_id):

    # from pin.api6.http import return_bad_request, return_json_data
    # try:
    #     token = ApiKey.objects.get(user_id=request.user.id)
    # except UnreadablePostError:
    #     return return_bad_request()

    # if settings.DEBUG:
    #     url = "http://127.0.0.1:8801/v7/like/item/?token={}"
    # else:
    #     url = "http://api.wisgoon.com/v7/like/item/?token={}"

    # url = url.format(token.key)
    # payload = {}
    # payload['item_id'] = item_id

    # # Get choices post
    # s = requests.Session()
    # res = s.post(url, data=payload, headers={'Connection': 'close'})

    # if res.status_code != 200:
    #     return return_bad_request(status=False)

    # try:
    #     data = json.loads(res.content)
    # except:
    #     return return_bad_request()
    # return return_json_data(data)
    post = post_item_json(post_id=int(item_id))
    if not post:
        return HttpResponseRedirect('/')

    import redis
    cur_user = request.user
    cur_user_id = request.user.id

    """ Check current user status """
    status = check_user_state(user_id=post['user']['id'],
                              current_user=cur_user)
    allow_like = status['status']

    if not allow_like:
        return HttpResponseRedirect('/')

    from models_redis import LikesRedis

    like, dislike, current_like = LikesRedis(post_id=item_id)\
        .like_or_dislike(user_id=cur_user_id,
                         post_owner=post['user']['id'],
                         user_ip=get_user_ip(request),
                         category=post['category']['id'],
                         date=post['timestamp'])

    redis_server = redis.Redis(settings.REDIS_DB_2, db=9)
    key = "cnt_like:user:{}:{}".format(cur_user_id,
                                       post['category']['id'])

    if like:
        user_act = 1
        redis_server.incr(key, 1)

    elif dislike:
        user_act = -1
        redis_server.incr(key, -1)

    if request.is_ajax():
        data = [{'likes': current_like, 'user_act': user_act}]
        return HttpResponse(json.dumps(data), content_type="text/html")
    else:
        return HttpResponseRedirect(reverse('pin-item', args=[post['id']]))


@login_required
@system_writable
def report(request, pin_id):

    try:
        post = Post.objects.only('id', 'user_id', 'report').get(id=pin_id)
    except Post.DoesNotExist:
        return HttpResponseRedirect('/')

    cur_user = request.user
    cur_user_id = request.user.id

    """ Check current user status """
    status = check_user_state(user_id=post.user_id,
                              current_user=cur_user)
    allow_report = status['status']

    if not allow_report:
        return HttpResponseRedirect('/')

    try:
        Report.objects.get(user=cur_user, post_id=post.id)
        created = False
    except Report.DoesNotExist:
        Report.objects.create(user=cur_user, post_id=post.id)
        created = True

    if created:
        if post.report == 9:
            post.status = 0
        post.report = post.report + 1
        post.save()
        status = True
        msg = _('Your report was saved.')
    else:
        status = False
        msg = _("You 've already reported this matter.")

    # TODO: add new report here @hossein
    # ridi azizam :D
    ReportedPost.post_report(post_id=post.id, reporter_id=cur_user_id)
    # End of hosseing work

    if request.is_ajax():
        data = {'status': status, 'message': msg}
        return HttpResponse(json.dumps(data),
                            content_type='application/json')
    else:
        return HttpResponseRedirect(reverse('pin-item', args=[post.id]))


@login_required
def comment_score(request, comment_id, score):
    score = int(score)
    scores = [1, 0]
    if score not in scores:
        return HttpResponse(_('There is error in scores.'))

    if score == 0:
        score = -1

    try:
        cm = Comments.objects.get(pk=comment_id)
        user = request.user
        cs, cd = Comments_score.objects.get_or_create(user=user, comment=cm)
        if score != cs.score:
            cs.score = score
            cs.save()

        sum_score = Comments_score.objects.filter(comment=cm)\
            .aggregate(Sum('score'))

        cm.score = sum_score['score__sum']
        cm.save()

        return HttpResponse(sum_score['score__sum'])

    except Comments.DoesNotExist:
        return HttpResponseRedirect('/')


@login_required
@system_writable
def delete(request, item_id):
    try:
        post = Post.objects.get(pk=item_id)
    except Post.DoesNotExist:
        msg = _("Post not found.")
        data = {'status': False, 'message': msg}
        return HttpResponse(json.dumps(data),
                            content_type='application/json')
        # return HttpResponse('0')

    # TODO samte ui moshkel dare
    if request.user.is_superuser or post.user == request.user:
        post_after_delete(post=post,
                          user=request.user,
                          ip_address=get_user_ip(request))
        post.delete()
        if request.is_ajax():
            msg = _("Successfully deleted post.")
            data = {'status': True, 'message': msg}
            return HttpResponse(json.dumps(data),
                                content_type='application/json')
            # return HttpResponse('1')
        return HttpResponseRedirect('/')

    return HttpResponse('0')


@login_required
def nop(request, item_id):
    """Image has no problem."""
    try:
        post = Post.objects.get(pk=item_id)
        if request.user.is_superuser:
            post.report = 0
            post.save()
            porn_feedback.delay(post_image=post.get_image_500()['url'])
            if request.is_ajax():
                return HttpResponse('1')
            return HttpResponseRedirect('/')

    except Post.DoesNotExist:
        return HttpResponse('0')

    return HttpResponse('0')


@csrf_exempt
@login_required
@system_writable
@user_passes_test(lambda u: u.is_active, login_url='/pin/you_are_deactive/')
def send_comment(request):
    cur_user = request.user
    from django.template.loader import render_to_string
    from django.template import RequestContext
    if request.method == 'POST':
        try:
            text = request.POST.get('text', None)
            post = int(request.POST.get('post', None))
        except UnreadablePostError:
            data = {'status': False,
                    'cnt_comments': 0,
                    'message': "Invalid parameters"}
            return JsonResponse(data)

        if text and post:
            post_json = post_item_json(post_id=post)
            if not post_json:
                data = {'status': False,
                        'cnt_comments': 0,
                        'message': "Post doest not exists"}
                return JsonResponse(data)

            """ Check current user status """
            status = check_user_state(user_id=post_json['user']['id'],
                                      current_user=cur_user)
            allow_comment = status['status']

            if not allow_comment:
                data = {'status': False,
                        'cnt_comments': post_json['cnt_comment'],
                        'message': "You do not have access to this post"}
                return JsonResponse(data)

            comment = Comments.objects\
                .create(object_pk_id=post_json['id'],
                        comment=text,
                        user=cur_user,
                        ip_address=get_user_ip(request))
            html = render_to_string('pin2/show_comment.html',
                                    {'comment': comment},
                                    context_instance=RequestContext(request))
            data = {'status': True,
                    'cnt_comments': post_json['cnt_comment'],
                    'message': html}
            return JsonResponse(data)

    data = {'status': False,
            'cnt_comments': 0,
            'message': "Post doest not exists"}
    return JsonResponse(data)


def you_are_deactive(request):
    return render(request, 'pin/you_are_deactive.html')


@login_required
@csrf_exempt
def sendurl(request):
    if request.method == "POST":
        post_values = request.POST.copy()
        form = PinForm(post_values)
        if form.is_valid():
            model = form.save(commit=False)

            image_url = model.image
            filename = image_url.split('/')[-1]
            filename = create_filename(filename)
            image_on = "{}/pin/{}/images/o/{}".\
                format(MEDIA_ROOT, settings.INSTANCE_NAME, filename)

            urllib.urlretrieve(image_url, image_on)

            model.image = "pin/{}/images/o/{}".\
                format(settings.INSTANCE_NAME, filename)
            model.timestamp = time()
            model.user = request.user
            model._user_ip = get_user_ip(request)
            model.save()

            next_url = reverse('pin-item', args=[model.id])

            return HttpResponseRedirect(next_url)
    else:
        form = PinForm()

    return render(request, 'pin/sendurl.html', {'form': form})


@login_required
@csrf_exempt
def a_sendurl(request):
    if request.method != "POST":
        return HttpResponse(0)

    url = request.POST['url']
    if url == '':
        return HttpResponse(0)

    images = get_images(url)
    if images == 0:
        return HttpResponse(0)

    return HttpResponse(json.dumps(images))


@login_required
@user_passes_test(lambda u: u.is_active, login_url='/pin/you_are_deactive/')
@csrf_exempt
@system_writable
def send(request):
    # TODO samte ui moshkel dare
    fpath = None
    filename = None
    status = False
    image_data = None
    image_type = None
    if request.method == "POST":
        try:
            post_values = request.POST.copy()
        except UnreadablePostError:
            if request.is_ajax():
                status = False
                next_url = reverse('pin-home')
                data = {
                    "location": next_url,
                    "status": status
                }
                return HttpResponse(json.dumps(data),
                                    content_type="application/json")
            else:
                msg = _("Error sending the image.")
                messages.add_message(request, messages.WARNING, msg)
                return HttpResponseRedirect('/')

        data_url_pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        image_data_post = post_values['image']
        if image_data_post:
            is_match = data_url_pattern.match(image_data_post)
            if is_match:
                image_data = is_match.group(2)
                image_type = is_match.group(1)
            else:
                if request.is_ajax():
                    status = False
                    next_url = reverse('pin-home')
                    data = {
                        "location": next_url,
                        "status": status
                    }
                    return HttpResponse(json.dumps(data),
                                        content_type="application/json")
                else:
                    msg = _("Error sending the image.")
                    messages.add_message(request, messages.WARNING, msg)
                    return HttpResponseRedirect('/')
        else:
            if request.is_ajax():
                status = False
                next_url = reverse('pin-home')
                data = {
                    "location": next_url,
                    "status": status
                }
                return HttpResponse(json.dumps(data),
                                    content_type="application/json")
            else:
                msg = _("Error sending the image.")
                messages.add_message(request, messages.WARNING, msg)
                return HttpResponseRedirect('/')

        if not image_data or len(image_data) == 0:
            pass

        image_data = base64.b64decode(image_data)
        f = "1.{}".format(image_type)
        filename = create_filename(f)

        fpath = "{}/pin/temp/o/{}".format(MEDIA_ROOT, filename)
        with open(fpath, 'wb') as dest:
            dest.write(image_data)

        post_values['image'] = fpath

        form = PinForm(post_values)

        if form.is_valid():
            model = form.save(commit=False)

            if fpath:
                image_o = fpath
            else:
                filename = model.image
                image_o = "{}/pin/temp/o/{}".format(MEDIA_ROOT, filename)

            image_on = "{}/pin/{}/images/o/{}".\
                format(MEDIA_ROOT, settings.INSTANCE_NAME, filename)

            try:
                copyfile(image_o, image_on)
            except IOError:
                msg = _("Error sending the image.")
                messages.add_message(request, messages.WARNING, msg)

                return HttpResponseRedirect('/pin/')

            model.image = "pin/{}/images/o/{}".\
                format(settings.INSTANCE_NAME, filename)
            model.timestamp = time()
            model.user = request.user
            model._user_ip = get_user_ip(request)
            model.save()

            next_url = reverse('pin-item', args=[model.id])
            status = True
            data = {
                "location": next_url,
                "status": status
            }
            return HttpResponse(json.dumps(data),
                                content_type="application/json")
    else:
        form = PinForm()

    category = Category.objects.all()

    if request.is_ajax():
        return render(request, 'pin/_send.html', {
            'form': form, 'category': category
        })
    else:
        return render(request, 'pin/send.html', {
            'form': form, 'category': category
        })


@login_required
@system_writable
def edit(request, post_id):
    try:
        post = Post.objects.get(pk=int(post_id))
    except Post.DoesNotExist:
        return HttpResponseRedirect('/pin/')

    if not request.user.is_superuser:
        if post.user.id != request.user.id:
            return HttpResponseRedirect('/pin/')

    if request.method == "POST":
        post_values = request.POST.copy()
        form = PinUpdateForm(post_values, instance=post)
        if form.is_valid():
            form.save()
            if request.is_ajax():
                return HttpResponse(_('Successfully updated.'))
            else:
                return HttpResponseRedirect(reverse('pin-item', args=[post_id]))
    else:
        form = PinUpdateForm(instance=post)

    if request.is_ajax():
        return render(request, 'pin2/_edit.html', {'form': form, 'post': post})
    else:
        return render(request, 'pin2/edit.html', {'form': form, 'post': post})


def save_upload(uploaded, filename, raw_data):
    try:
        path = "%s/pin/temp/o/%s" % (MEDIA_ROOT, filename)
        from io import FileIO, BufferedWriter
        with BufferedWriter(FileIO(path, "wb")) as dest:

            if raw_data:
                foo = uploaded.read(1024)
                while foo:
                    dest.write(foo)
                    foo = uploaded.read(1024)

            else:
                for c in uploaded.chunks():
                    dest.write(c)
            return True
    except IOError:
        return False


@csrf_exempt
def upload(request):
    if request.method == "POST":
        if request.is_ajax():
            upload = request
            is_raw = True
            try:
                filename = request.GET['qqfile']
            except KeyError:
                return HttpResponseBadRequest(_("AJAX request not valid"))
        else:
            is_raw = False
            if len(request.FILES) == 1:
                upload = request.FILES.values()[0]
            else:
                raise Http404(_("Bad Upload"))
            filename = upload.name

        filename = create_filename(filename)
        success = save_upload(upload, filename, is_raw)
        if success:
            image_original = "{}pin/temp/o/{}".format(MEDIA_URL, filename)
            image_o = "{}/pin/temp/o/{}".format(MEDIA_ROOT, filename)
            image_th = "{}pin/temp/t/{}".format(MEDIA_URL, filename)
            image_t = "{}/pin/temp/t/{}".format(MEDIA_ROOT, filename)

            image_500_th = "{}pin/temp/t/{}".format(
                MEDIA_URL, filename.replace('.', '_500.'))
            image_500_t = "{}/pin/temp/t/{}".format(
                MEDIA_ROOT, filename.replace('.', '_500.'))

            pin_image.resize(image_o, image_t, 99)
            pin_image.resize(image_o, image_500_t, 500)

        ret_json = {
            'success': success,
            'file_o': image_original,
            'file_t': image_th,
            'file_low': image_500_th,
            'file': filename
        }
        return HttpResponse(json.dumps(ret_json))

    return HttpResponseBadRequest("Bad request")


@login_required
def show_notify(request):
    user_id = request.user.id
    NotificationRedis(user_id=user_id).clear_notif_count()
    notif = NotificationRedis(user_id=user_id)\
        .get_notif()

    nl = []
    for n in notif:
        anl = {}
        anl['ob'] = post_item_json(post_id=n.post)
        if not anl['ob']:
            if n.type == 4:
                anl['po'] = n.post_image
            elif n.type in [10, 7]:
                anl['po'] = n.last_actor
                anl['pending'] = FollowRequest.objects\
                    .filter(user_id=user_id,
                            target_id=n.last_actor)\
                    .exists()
            else:
                continue
        # try:
            # anl['ob'] = image['images']['original']
            # anl['po'] = Post.objects.only('image').get(pk=n.post)
        # except Post.DoesNotExist:
        anl['id'] = n.post
        anl['type'] = n.type
        anl['actor'] = n.last_actor

        nl.append(anl)
    return render(request, 'pin2/notify.html', {'notif': nl})


@login_required
def notif_user(request):
    offset = int(request.GET.get('older', 0))
    follow_requests = {}
    user = request.user
    user_id = user.id
    is_private = user.profile.is_private
    notifications = NotificationRedis(user_id=user_id)\
        .get_notif(start=offset)
    nl = []
    last_date = None
    for notif in notifications:
        anl = {}
        anl['ob'] = post_item_json(post_id=notif.post)
        anl['pending'] = False
        if not anl['ob']:
            if notif.type == 4:
                anl['po'] = notif.post_image
            elif notif.type in [10, 7]:
                anl['po'] = notif.last_actor
                anl['pending'] = FollowRequest.objects\
                    .filter(user_id=user_id,
                            target_id=notif.last_actor)\
                    .exists()
            else:
                continue
        # try:
            # anl['po'] = Post.objects.only('image').get(pk=notif.post)
        # except Post.DoesNotExist:
        anl['id'] = notif.post
        anl['type'] = notif.type
        anl['actor'] = notif.last_actor
        anl['pid'] = notif.id

        if notif.date:
            last_date = notif.date

        nl.append(anl)
    if is_private:
        """ Get follow request """
        follow_requests = FollowRequest.objects\
            .filter(target_id=user_id)

        cnt_requests = follow_requests.count()
        if cnt_requests > 0:
            last_follow_req = follow_requests.order_by('-id')[0]
            user_obj = get_simple_user_object(last_follow_req.user.id)

            follow_requests = {'user': user_obj,
                               'cnt_requests': cnt_requests}

    if request.is_ajax():
        return render(request, 'pin2/_notif.html', {
            'notif': nl,
            'offset': last_date,
            'is_private': is_private,
            'follow_requests': follow_requests
        })
    else:
        return render(request, 'pin2/notif_user.html', {
            'notif': nl,
            'offset': last_date,
            'is_private': is_private,
            'follow_requests': follow_requests
        })


@login_required
def notif_following(request):
    notif_data = ActivityRedis(user_id=request.user.id).get_activity()
    return render(request, 'pin2/notif_user_following.html', {
        'notif': notif_data,
        'page': 'follow_notif',
    })


@login_required
def follow_requests(request):
    offset = int(request.GET.get('offset', 0))
    limit = 20
    follow_req = []

    follow_request = FollowRequest.objects\
        .filter(target=request.user)\
        .order_by('-id')[offset:offset + limit]

    for req in follow_request:
        data = {}
        data['user'] = get_simple_user_object(req.user.id)
        follow_req.append(data)

    if request.is_ajax():
        return render(request, 'pin2/_follow_requests.html', {
            'offset': offset + limit,
            'follow_requests': follow_req
        })
    else:
        return render(request, 'pin2/user_follow_requests.html', {
            'offset': offset + limit,
            'follow_requests': follow_req
        })


@system_writable
@login_required
def remove_follow_req(request, following):

    current_user_id = request.user.id
    cnt_followers = 0
    if int(following) == current_user_id:
        return HttpResponseRedirect(reverse('pin-home'))
    try:
        target = User.objects.get(pk=int(following))
        FollowRequest.objects\
            .filter(user_id=current_user_id,
                    target=target)\
            .delete()
        cnt_followers = target.profile.cnt_followers
    except:
        pass
    data = {
        'status': True,
        'is_follow': False,
        'message': _("Successfully remove your follow request"),
        'pending': False,
        'count': cnt_followers
    }
    return HttpResponse(json.dumps(data),
                        content_type='application/json')


@csrf_exempt
@system_writable
@login_required
def accept_follow(request):

    data = {}
    user_id = request.POST.get('user_id', None)
    accepted = bool(int(request.POST.get('accepted', 0)))
    target_user = request.user

    if not user_id:
        msg = _("Invalid parameters")
        return HttpResponse(json.dumps({'message': msg,
                                        'status': False}),
                            status=404,
                            content_type='application/json')
    is_req = FollowRequest.objects.filter(user_id=int(user_id),
                                          target=target_user)
    if is_req.exists():
        if accepted:
            instance = Follow.objects.create(follower_id=int(user_id),
                                             following=target_user)
            # Send notification
            from pin.actions import send_notif_bar
            send_notif_bar(user=instance.follower_id,
                           type=7,
                           post=None,
                           actor=instance.following_id)
            is_req.delete()
            status = True
            message = _('Your connection successfully established.')
            accepted = 1
        else:
            is_req.delete()
            status = True
            message = _('Decline follow request')
            accepted = 0

        data = {'status': status,
                'message': message,
                'accepted': accepted}
        return HttpResponse(json.dumps(data), content_type='application/json')
    else:
        msg = "Follow request not exists"
        return HttpResponse(json.dumps({'message': msg,
                                        'status': False}),
                            status=404,
                            content_type='application/json')


@login_required
def notif_all(request):
    notif = Notif.objects.order_by('-date')[:20]

    nl = []
    idis = []
    for n in notif:
        anl = {}
        image = post_item_json(post_id=notif.post, fields=['images'])
        if image:
            po = anl['po'] = image['images']['original']
            if po not in idis:
                idis.append(po)
            else:
                continue

        anl['id'] = n.post
        anl['type'] = n.type
        anl['actors'] = n.last_actors

        nl.append(anl)

    return render(request, 'pin/notif_user.html', {'notif': nl})


@login_required
@system_writable
def inc_credit(request):

    if request.method == "POST":

        amount = request.POST.get('amount', 0)
        if not amount:
            return HttpResponseRedirect(reverse('pin-inc-credit'))

        bill = Bills.objects.create(user=request.user, amount=amount)
        call_back_url = '{}{}'.format(
            SITE_URL, reverse('pin-verify-payment', args=[bill.id]))

        url = 'https://ir.zarinpal.com/pg/services/WebGate/wsdl'
        client = Client(url)
        desc = _("bill payment")

        data = {'MerchantID': MERCHANT_ID,
                'Amount': amount,
                'Description': desc,
                'Email': str(request.user.email),
                'Mobile': str(request.user.id),
                'CallbackURL': call_back_url}

        result = client.service.PaymentRequest(**data)

        if result['Status'] == 100:
            url = 'https://www.zarinpal.com/pg/StartPay/{}'\
                .format(str(result['Authority']))
            return HttpResponseRedirect(url)
        else:
            msg = 'Error when connecting to the database server'
            messages.error(request, _(msg))
            return HttpResponseRedirect(reverse('pin-inc-credit'))
    return render(request, 'pin2/credit/inc_credit.html', {

    })


def verify_payment(request, bill_id):
    bill = Bills.objects.get(id=bill_id)

    authority = request.GET.get('Authority', False)
    status = request.GET.get('Status', False)

    if authority and status == 'OK':

        url = 'https://ir.zarinpal.com/pg/services/WebGate/wsdl'
        client = Client(url)
        data = {
            'MerchantID': MERCHANT_ID,
            'Amount': bill.amount,
            'Authority': authority
        }

        result = client.service.PaymentVerification(**data)

        if result['Status'] == 100:
            bill.trans_id = str(result['RefID'])
            bill.status = 1
            bill.save()
            # UserMeta.objects(user=bill.user).update(inc__credit=bill.amount)
            p = bill.user.profile
            p.inc_credit(amount=bill.amount)
            message = "Payment was successful. Your tracking code {}"\
                .format(str(result['RefID']))
            messages.success(request, _(message))

            from pin.model_mongo import MonthlyStats
            MonthlyStats.log_hit(object_type=MonthlyStats.BILL)

            return HttpResponseRedirect(reverse('pin-inc-credit'))
        else:
            message = 'Payment unsuccessful , the amount deducted from your account the\
                       bank returns .'
            messages.error(request,
                           _(message))
            return HttpResponseRedirect(reverse('pin-inc-credit'))

    else:
        return HttpResponseRedirect(reverse('pin-inc-credit'))


@login_required
@system_writable
def save_as_ads(request, post_id):

    p = post_item_json(post_id=post_id)
    profile = request.user.profile

    """ Check current user status """
    # cur_user = request.user
    # status = check_user_state(user_id=p['user']['id'],
    #                           current_user=cur_user)
    # allow_promote = status['status']

    # if not allow_promote:
    #     return HttpResponseRedirect('/')
    cur_user_id = request.user.id

    try:
        post_owner_profile = Profile.objects.only('is_private')\
            .get(user_id=p['user']['id'])
        is_private = post_owner_profile.is_private
    except:
        is_private = False

    if is_private:
        msg = _('This profile is private')
        messages.error(request, _(msg))
        return HttpResponseRedirect('/')

    if request.method == "POST":
        mode = int(request.POST.get('mode'))
        mode_price = Ad.TYPE_PRICES[mode]
        if profile.credit >= int(mode_price):
            try:
                Ad.objects.get(post=int(post_id), ended=False)
                messages.error(request, _("This post has been advertised"))
            except Exception, Ad.DoesNotExist:
                profile.dec_credit(amount=int(mode_price))

                Ad.objects.create(user_id=cur_user_id,
                                  post_id=int(post_id),
                                  ads_type=mode,
                                  start=datetime.datetime.now(),
                                  ip_address=get_user_ip(request))
                msg = "Post of you was advertised successfully ."
                messages.success(request, _(msg))

        else:
            msg = "Your account credit is not enough for advertise "
            messages.error(request, _(msg))

    return render(request, 'pin2/credit/save_as_ads.html', {
        'post': p,
        'page': 'save_as_ad',
        'user_meta': profile,
        'Ads': Ad,
    })


@login_required
@system_writable
def block_action(request, user_id):

    user = request.user
    action = request.GET.get('action', False)

    if not action:
        data = {'status': False,
                'type': 'None',
                'message': _('There is no action')}
    else:
        if action == "block":
            Block.block_user(user_id=user.id, blocked_id=user_id)
            data = {'status': True,
                    'type': 'block',
                    'message': _('This user was blocked successfully')}

        elif action == "unblock":
            Block.unblock_user(user_id=user.id, blocked_id=user_id)
            data = {'status': True,
                    'type': 'unblock',
                    'message': _('This user was unblocked successfully')}

        else:
            data = {'status': False,
                    'type': 'None',
                    'message': _('The data entered is not valid')}

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def blocked_list(request):
    older = request.POST.get('older', False)

    if older:
        blocked_list = Block.objects.filter(user_id=request.user.id,
                                            id__lt=older)\
            .order_by('-id')[:16]
    else:
        blocked_list = Block.objects.filter(user_id=request.user.id)\
            .order_by('-id')[:16]

    if request.is_ajax():
        if blocked_list.exists():
            return render(request, 'pin2/profile/_blocked_list_item.html', {
                'blocked_list': blocked_list,
                'user': request.user
            })
        else:
            return HttpResponse(0)
    profile = request.user.profile
    return render(request, 'pin2/profile/blocked_list.html', {
        'blocked_list': blocked_list,
        'profile': profile,
        'cur_user': request.user,
        'is_private': profile.is_private
    })


@login_required
def promotion_list(request):
    older = request.POST.get('older', False)

    if older:
        promotion_list = Ad.objects\
            .filter(Q(user=request.user) |
                    Q(owner=request.user),
                    id__lt=older).order_by('-id')[:16]
    else:
        promotion_list = Ad.objects\
            .filter(Q(user=request.user) |
                    Q(owner=request.user)).order_by('-id')[:16]

    if request.is_ajax():
        if promotion_list.exists():
            return render(request, 'pin2/profile/_promotion_item.html', {
                'promotion_list': promotion_list,
                'user': request.user
            })
        else:
            return HttpResponse(0)
    profile = request.user.profile
    return render(request, 'pin2/profile/promotion.html', {
        'promotion_list': promotion_list,
        'profile': profile,
        'cur_user': request.user,
        'is_private': profile.is_private
    })


@login_required
def user_notif(request):
    notif_list = []
    before = int(request.GET.get("before", 0))

    notifications = UserNotification(user_id=11)\
        .get_obj_notif(before=before)
    follow_list = ['follow', 'request follow', 'accept follow']
    if notifications:
        for notification in notifications:

            '''update notification is_seen
                mark_activities(self, activity_ids, seen=True, read=False) by
                default'''
            notif_ids = notification.activity_ids
            MyNotificationFeed(request.user.id).mark_activities(notif_ids)

            if notification.verb.infinitive == 'create':
                notif = notif_simple_json(notification=notification,
                                          user=False)

            elif notification.verb.infinitive == 'comment':
                if len(notification.actor_ids) == 1:
                    notif = notif_simple_json(notification=notification,
                                              text=True)
                else:
                    notif = notif_simple_json(notification=notification)

            elif notification.verb.infinitive == 'like':
                notif = notif_simple_json(notification=notification)

            elif notification.verb.infinitive in follow_list:
                notif = notif_simple_json(notification=notification,
                                          post=False)

            notif_list.append(notif)

    return JsonResponse(notif_list, safe=False)

    # return render(request, 'pin2/new_notif.html', {
    #     'notif_list': notif_list,
    # })
