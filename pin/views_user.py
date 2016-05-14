# -*- coding: utf-8 -*-
from time import time
import re
import base64
import json
import datetime
import urllib
from django.db.models import Q
from shutil import copyfile

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db.models import Sum
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext as _
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseBadRequest, Http404

from pin.crawler import get_images
from pin.forms import PinForm, PinUpdateForm
from pin.models import Post, Stream, Follow, Ad, Block, UserPermissions,\
    Report, Comments, Comments_score, Category, Bills2 as Bills, ReportedPost

from pin.model_mongo import Notif
from pin.models_redis import ActivityRedis, NotificationRedis
import pin_image
from pin.tools import create_filename, get_user_ip, get_request_pid,\
    check_block, post_after_delete, get_post_user_cache

from pin.tasks import porn_feedback
from pin.api6.tools import post_item_json

from suds.client import Client

# User = get_user_model()
MEDIA_ROOT = settings.MEDIA_ROOT
MEDIA_URL = settings.MEDIA_URL
MERCHANT_ID = settings.MERCHANT_ID
SITE_URL = settings.SITE_URL


@login_required
def following(request):
    pid = get_request_pid(request)
    pl = Post.user_stream_latest(pid=pid, user_id=request.user.id)

    arp = []
    for pll in pl:
        pll_id = int(pll)
        ob = post_item_json(pll_id, cur_user_id=request.user.id)
        if ob:
            arp.append(ob)

    latest_items = arp

    sorted_objects = latest_items

    if request.is_ajax():
        if latest_items:
            return render(request,
                          'pin2/_items_2_v6.html',
                          {'latest_items': sorted_objects})
        else:
            return HttpResponse(0)
    else:
        return render(request,
                      'pin2/following.html', {
                          'page': 'following',
                          'latest_items': sorted_objects
                      })


@login_required
def follow(request, following, action):
    message = ''
    status = ''
    if int(following) == request.user.id:
        return HttpResponseRedirect(reverse('pin-home'))

    try:
        following = User.objects.get(pk=int(following))
    except User.DoesNotExist:
        return HttpResponseRedirect('/')

    try:
        follow, created = Follow.objects.get_or_create(follower=request.user,
                                                       following=following)
    except Exception, e:
        follow = Follow.objects.filter(follower=request.user,
                                       following=following)[0]
        created = False
        print str(e)

    if int(action) == 0 and follow:
        follow.delete()
        Stream.objects.filter(following=following, user=request.user).delete()
        message = _('Your connection was successfully shut down')
        status = False
    elif created:
        message = _('Your connection successfully established.')
        status = True

    if request.is_ajax():
        data = {
            'status': status,
            'message': message,
            'count': following.profile.cnt_followers
        }
        return HttpResponse(json.dumps(data), content_type='application/json')
    return HttpResponseRedirect(reverse('pin-user', args=[following.id]))


@login_required
def like(request, item_id):
    try:
        post = get_post_user_cache(post_id=item_id)
    except Post.DoesNotExist:
        return HttpResponseRedirect('/')

    from models_redis import LikesRedis
    like, dislike, current_like = LikesRedis(post_id=item_id)\
        .like_or_dislike(user_id=request.user.id,
                         post_owner=post.user_id,
                         user_ip=get_user_ip(request),
                         category=post.category_id)

    if like:
        user_act = 1
    elif dislike:
        user_act = -1

    if request.is_ajax():
        data = [{'likes': current_like, 'user_act': user_act}]
        return HttpResponse(json.dumps(data), content_type="text/html")
    else:
        return HttpResponseRedirect(reverse('pin-item', args=[post.id]))


@login_required
def report(request, pin_id):
    try:
        permission = UserPermissions.objects.get(user=request.user)
    except Exception, e:
        print str(e), "function report permission"

    if permission.report:

        try:
            post = Post.objects.get(id=pin_id)
        except Post.DoesNotExist:
            return HttpResponseRedirect('/')

        try:
            Report.objects.get(user=request.user, post=post)
            created = False
        except Report.DoesNotExist:
            Report.objects.create(user=request.user, post=post)
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
        ReportedPost.post_report(post_id=post.id, reporter_id=request.user.id)
        # End of hosseing work

        if request.is_ajax():
            data = {'status': status, 'message': msg}
            return HttpResponse(json.dumps(data), content_type='application/json')
        else:
            return HttpResponseRedirect(reverse('pin-item', args=[post.id]))
    else:
        return HttpResponse('message : user report is blocked')


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
def delete(request, item_id):
    try:
        post = Post.objects.get(pk=item_id)
    except Post.DoesNotExist:
        return HttpResponse('0')

    if request.user.is_superuser or post.user == request.user:
        post_after_delete(post=post,
                          user=request.user,
                          ip_address=get_user_ip(request))
        post.delete()
        if request.is_ajax():
            return HttpResponse('1')
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
@user_passes_test(lambda u: u.is_active, login_url='/pin/you_are_deactive/')
def send_comment(request):
    try:
        permission = UserPermissions.objects.get(user=request.user)
    except Exception, e:
        print str(e), "function send_comment permission"

    print permission
    if permission.comment:

        if request.method == 'POST':
            text = request.POST.get('text', None)
            post = request.POST.get('post', None)

            if text and post:
                post = get_object_or_404(Post, pk=post)
                if check_block(user_id=post.user_id, blocked_id=request.user.id):
                    return HttpResponseRedirect('/')

                comment = Comments.objects.create(object_pk_id=post.id,
                                                  comment=text,
                                                  user=request.user,
                                                  ip_address=get_user_ip(request))
                return render(request, 'pin2/show_comment.html', {
                    'comment': comment
                })

        return HttpResponse('error')
    else:
        return HttpResponse('message : user is blocked')


def you_are_deactive(request):
        return render(request, 'pin/you_are_deactive.html')


@login_required
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
def send(request):
    fpath = None
    filename = None
    status = False
    if request.method == "POST":
        post_values = request.POST.copy()
        data_url_pattern = re.compile('data:image/(png|jpeg);base64,(.*)$')
        image_data_post = post_values['image']
        image_data = data_url_pattern.match(image_data_post).group(2)
        image_type = data_url_pattern.match(image_data_post).group(1)

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
            return HttpResponse(json.dumps(data), content_type="application/json")

            return HttpResponseRedirect(next_url)
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
def edit(request, post_id):
    try:
        post = Post.objects.get(pk=int(post_id))
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
            return render(request, 'pin/_edit.html', {'form': form, 'post': post})
        else:
            return render(request, 'pin/edit.html', {'form': form, 'post': post})
    except Post.DoesNotExist:
        return HttpResponseRedirect('/pin/')


def save_upload(uploaded, filename, raw_data):
    try:
        from io import FileIO, BufferedWriter
        with BufferedWriter(FileIO("%s/pin/temp/o/%s" % (MEDIA_ROOT, filename), "wb")) as dest:

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

            image_500_th = "{}pin/temp/t/{}".format(MEDIA_URL, filename.replace('.', '_500.'))
            image_500_t = "{}/pin/temp/t/{}".format(MEDIA_ROOT, filename.replace('.', '_500.'))

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
    NotificationRedis(user_id=request.user.id).clear_notif_count()
    notif = NotificationRedis(user_id=request.user.id)\
        .get_notif()

    nl = []
    for n in notif:
        anl = {}
        try:
            anl['po'] = Post.objects.only('image').get(pk=n.post)
        except Post.DoesNotExist:
            if n.type == 4:
                anl['po'] = n.post_image
            elif n.type == 10:
                anl['po'] = n.last_actor
            else:
                continue
        anl['id'] = n.post
        anl['type'] = n.type
        anl['actor'] = n.last_actor

        nl.append(anl)
    return render(request, 'pin2/notify.html', {'notif': nl})


@login_required
def notif_user(request):
    offset = int(request.GET.get('older', 0))

    notifications = NotificationRedis(user_id=request.user.id)\
        .get_notif(start=offset)
    nl = []
    for notif in notifications:
        anl = {}
        try:
            anl['po'] = Post.objects.only('image').get(pk=notif.post)
        except Post.DoesNotExist:
            if notif.type == 4:
                anl['po'] = notif.post_image
            elif notif.type == 10:
                anl['po'] = notif.last_actor
            else:
                continue
        anl['id'] = notif.post
        anl['type'] = notif.type
        anl['actor'] = notif.last_actor
        anl['pid'] = notif.id

        nl.append(anl)

    if request.is_ajax():
        return render(request, 'pin/_notif.html', {
            'notif': nl,
            'offset': offset + 20
        })
    else:
        return render(request, 'pin/notif_user.html', {
            'notif': nl,
            'offset': offset + 20
        })


@login_required
def notif_following(request):
    notif_data = ActivityRedis(user_id=request.user.id).get_activity()
    return render(request, 'pin2/notif_user_following.html', {
        'notif': notif_data,
        'page': 'follow_notif',
    })


@login_required
def notif_all(request):
    notif = Notif.objects.order_by('-date')[:20]

    nl = []
    idis = []
    for n in notif:
        anl = {}
        try:
            po = anl['po'] = Post.objects.values('image').get(pk=n.post)['image']
            if po not in idis:
                idis.append(po)
            else:
                continue
        except Post.DoesNotExist:
            continue
        anl['id'] = n.post
        anl['type'] = n.type
        anl['actors'] = n.last_actors

        nl.append(anl)

    return render(request, 'pin/notif_user.html', {'notif': nl})


@login_required
def inc_credit(request):
    if request.method == "POST":

        amount = request.POST.get('amount', 0)
        if not amount:
            return HttpResponseRedirect(reverse('pin-inc-credit'))

        bill = Bills.objects.create(user=request.user, amount=amount)
        callBackUrl = '%s%s' % (SITE_URL, reverse('pin-verify-payment', args=[bill.id]))

        url = 'https://ir.zarinpal.com/pg/services/WebGate/wsdl'
        client = Client(url)
        desc = _("bill payment")

        data = {'MerchantID': MERCHANT_ID,
                'Amount': amount,
                'Description': desc,
                'Email': str(request.user.email),
                'Mobile': str(request.user.id),
                'CallbackURL': callBackUrl}

        result = client.service.PaymentRequest(**data)

        if result['Status'] == 100:
            url = 'https://www.zarinpal.com/pg/StartPay/%s' % str(result['Authority'])
            return HttpResponseRedirect(url)
        else:
            messages.error(request, _('Error when connecting to the database server'))
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
            message = "Payment was successful. Your tracking code %s" % str(result['RefID'])
            messages.success(request, _(message))

            from pin.model_mongo import MonthlyStats
            MonthlyStats.log_hit(object_type=MonthlyStats.BILL)

            return HttpResponseRedirect(reverse('pin-inc-credit'))
        else:
            message = 'Payment unsuccessful , the amount deducted from your account the bank returns .'
            messages.error(request,
                           _(message))
            return HttpResponseRedirect(reverse('pin-inc-credit'))

    else:
        return HttpResponseRedirect(reverse('pin-inc-credit'))


@login_required
def save_as_ads(request, post_id):
    p = Post.objects.get(id=post_id)
    profile = request.user.profile

    if request.method == "POST":
        mode = int(request.POST.get('mode'))
        mode_price = Ad.TYPE_PRICES[mode]
        if profile.credit >= int(mode_price):
            try:
                Ad.objects.get(post=int(post_id), ended=False)
                messages.error(request, _("This post has been advertised"))
            except Exception, Ad.DoesNotExist:
                profile.dec_credit(amount=int(mode_price))

                Ad.objects.create(user_id=request.user.id,
                                  post_id=int(post_id),
                                  ads_type=mode,
                                  start=datetime.datetime.now(),
                                  ip_address=get_user_ip(request))

                messages.success(request,
                                 _("Post of you was advertised successfully ."))

        else:
            messages.error(request,
                           _("Your account credit is not enough for advertise "))

    return render(request, 'pin2/credit/save_as_ads.html', {
        'post': p,
        'user_meta': profile,
        'Ads': Ad,
    })


@login_required
def block_action(request, user_id):
    user = request.user
    action = request.GET.get('action', False)

    if not action:
        data = {'status': False, 'type': 'None', 'message': _('There is no action')}
    else:
        if action == "block":
            Block.block_user(user_id=user.id, blocked_id=user_id)
            data = {'status': True, 'type': 'block',
                    'message': _('This user was blocked successfully')}
        elif action == "unblock":
            Block.unblock_user(user_id=user.id, blocked_id=user_id)
            data = {'status': True, 'type': 'unblock',
                    'message': _('This user was unblocked successfully')}
        else:
            data = {'status': False, 'type': 'None',
                    'message': _('The data entered is not valid')}

    return HttpResponse(json.dumps(data), content_type="application/json")


@login_required
def blocked_list(request):
    older = request.POST.get('older', False)

    if older:
        blocked_list = Block.objects.filter(user_id=request.user.id, id__lt=older).order_by('-id')[:16]
    else:
        blocked_list = Block.objects.filter(user_id=request.user.id).order_by('-id')[:16]

    if request.is_ajax():
        if blocked_list.exists():
            return render(request, 'pin2/profile/_blocked_list_item.html', {
                'blocked_list': blocked_list,
                'user': request.user
            })
        else:
            return HttpResponse(0)

    return render(request, 'pin2/profile/blocked_list.html', {
        'blocked_list': blocked_list,
        'profile': request.user.profile,
        'cur_user': request.user
    })


@login_required
def promotion_list(request):
    older = request.POST.get('older', False)

    if older:
        promotion_list = Ad.objects.filter(Q(user=request.user) | Q(owner=request.user), id__lt=older).order_by('-id')[:16]
    else:
        promotion_list = Ad.objects.filter(Q(user=request.user) | Q(owner=request.user)).order_by('-id')[:16]

    if request.is_ajax():
        if promotion_list.exists():
            return render(request, 'pin2/profile/_promotion_item.html', {
                'promotion_list': promotion_list,
                'user': request.user
            })
        else:
            return HttpResponse(0)

    return render(request, 'pin2/profile/promotion.html', {
        'promotion_list': promotion_list,
        'profile': request.user.profile,
        'cur_user': request.user
    })
