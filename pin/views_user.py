# -*- coding: utf-8 -*-
from time import time
import json
import datetime
import urllib
from shutil import copyfile

from instagram.client import InstagramAPI

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Sum
from django.http import HttpResponse, HttpResponseRedirect,\
    HttpResponseBadRequest, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from pin.crawler import get_images
from pin.forms import PinForm, PinUpdateForm
from pin.models import Post, Stream, Follow, Likes,\
    Report, Comments, Comments_score, Category

from pin.model_mongo import Notif, UserMeta

import pin_image
from pin.tools import get_request_timestamp, create_filename,\
    get_user_ip, get_request_pid, check_block

from user_profile.models import Profile

from suds.client import Client

MEDIA_ROOT = settings.MEDIA_ROOT
MERCHANT_ID = settings.MERCHANT_ID

def parse_instagram_update(update):
    instagram_userid = update['object_id']
    users = models.User.all().filter('instagram_userid =', instagram_userid).fetch(10)
    if len(users) == 0:
        logging.info('Didnt find matching users for this update')
    for user in users:
        deferred.defer(fetch_instagram_for_user, user.get_id(), _queue='instagram', _countdown=120)

def hook_insta(request):
    from instagram import client, subscriptions

    mode         = request.GET.get('hub.mode')
    challenge    = request.GET.get('hub.challenge')
    verify_token = request.GET.get('hub.verify_token')
    if challenge: 
        return HttpResponse(challenge)
    else:
        reactor = subscriptions.SubscriptionsReactor()
        reactor.register_callback(subscriptions.SubscriptionType.USER, parse_instagram_update)

        x_hub_signature = request.headers.get('X-Hub-Signature')
        raw_response    = request.data
        try:
            reactor.process(INSTAGRAM_SECRET, raw_response, x_hub_signature)
        except subscriptions.SubscriptionVerifyError:
            return HttpResponse('Instagram signature mismatch')
    return HttpResponse('Parsed instagram')

@login_required
def get_insta(request):
    client_id = "ecb7cbd35a11467fb2cf558583a44047"
    client_secret = "74e85dfb6b904ac68139a93a9b047247"
    redirect_uri = "http://127.0.0.1:8000/pin/get_insta/"
    scope = ["basic"]

    try:
        um = UserMeta.objects.get(user=int(request.user.id))
        access_token = um.insta_token
        insta_id = um.insta_id

        api = InstagramAPI(client_id=client_id, client_secret=client_secret)

    except UserMeta.DoesNotExist:
        api = InstagramAPI(client_id=client_id, client_secret=client_secret, redirect_uri=redirect_uri)

        redirect_uri = api.get_authorize_login_url(scope = scope)
        print redirect_uri
        code = request.GET.get('code')
        if not code:
            return HttpResponseRedirect(redirect_uri)
        print code

        # api = InstagramAPI(access_token=access_token)
        access_token = api.exchange_code_for_access_token(code)
        print access_token, dir(access_token)
        insta_id = access_token[1]["id"]
        access_token = access_token[0]
        UserMeta.objects(user=int(request.user.id))\
            .update(set__insta_token=access_token,
                    set__insta_id=insta_id,
                    upsert=True)

    from instagram import client
    instagram_client = client.InstagramAPI(client_id=client_id, client_secret=client_secret)
    callback_url = 'http://wisgoon.com/pin/hook/instagram'
    instagram_client.create_subscription(object='user', aspect='media', callback_url=callback_url)


@login_required
def following(request):
    pid = get_request_pid(request)
    pl = Post.user_stream_latest(pid=pid, user_id=request.user.id)

    arp = []
    for pll in pl:
        try:
            arp.append(Post.objects.get(id=pll))
        except:
            pass

    latest_items = arp

    sorted_objects = latest_items

    if request.is_ajax():
        if latest_items:
            return render(request,
                          'pin2/_items_2.html',
                          {'latest_items': sorted_objects})
        else:
            return HttpResponse(0)
    else:
        return render(request,
                      'pin2/following.html',
                      {'latest_items': sorted_objects})


@login_required
def follow(request, following, action):
    if int(following) == request.user.id:
        return HttpResponseRedirect(reverse('pin-home'))

    try:
        following = User.objects.get(pk=int(following))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('pin-user', args=[following.id]))

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
    elif created:
        posts = Post.objects.only('timestamp').filter(user=following)\
            .order_by('-timestamp')[:100]

        for post in posts:
            s, created = Stream.objects.get_or_create(post=post,
                                                      user=request.user,
                                                      date=post.timestamp,
                                                      following=following)
            # print "post", post.id, s, created

    return HttpResponseRedirect(reverse('pin-user', args=[following.id]))
    

@login_required
def like(request, item_id):
    try:
        post = Post.objects.get(pk=item_id)
    except Post.DoesNotExist:
        return HttpResponseRedirect('/')

    current_like = post.cnt_likes()

    try:
        liked = Likes.objects.get(user=request.user, post=post)
        created = False
    except Likes.DoesNotExist:
        liked = Likes.objects.create(user=request.user, post=post)
        created = True

    if created:
        current_like = current_like + 1
        user_act = 1
    elif liked:
        current_like = current_like - 1
        Likes.objects.get(user=request.user, post=post).delete()
        user_act = -1

    if request.is_ajax():
        data = [{'likes': current_like, 'user_act': user_act}]
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseRedirect(reverse('pin-item', args=[post.id]))

    


@login_required
def report(request, pin_id):
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
        msg = 'گزارش شما ثبت شد.'
    else:
        status = False
        msg = 'شما قبلا این مطلب را گزارش داده اید.'

    if request.is_ajax():
        data = [{'status': status, 'msg': msg}]
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseRedirect(reverse('pin-item', args=[post.id]))


@login_required
def comment_score(request, comment_id, score):
    score = int(score)
    scores = [1, 0]
    if score not in scores:
        return HttpResponse('error in scores')

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
        if request.user.is_superuser or post.user == request.user:
            post.delete()
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
    if request.method == 'POST':
        text = request.POST.get('text', None)
        post = request.POST.get('post', None)
        if text and post:
            post = get_object_or_404(Post, pk=post)
            if check_block(user_id=post.user_id, blocked_id=request.user.id):
                return HttpResponseRedirect('/')
            Comments.objects.create(object_pk=post,
                                    comment=text,
                                    user=request.user,
                                    ip_address=get_user_ip(request))

            return HttpResponseRedirect(reverse('pin-item', args=[post.id]))

    return HttpResponse('error')


def you_are_deactive(request):
    return render(request, 'pin/you_are_deactive.html')


@login_required
def sendurl(request):
    if request.method == "POST":
        post_values = request.POST.copy()
        # tags = post_values['tags']
        # post_values['tags'] = tags[tags.find("[")+1:tags.find("]")]
        form = PinForm(post_values)
        if form.is_valid():
            model = form.save(commit=False)

            image_url = model.image
            filename = image_url.split('/')[-1]
            filename = create_filename(filename)
            image_on = "%s/pin/images/o/%s" % (MEDIA_ROOT, filename)

            urllib.urlretrieve(image_url, image_on)

            model.image = "pin/images/o/%s" % (filename)
            model.timestamp = time()
            model.user = request.user
            model.save()

            form.save_m2m()

            if model.status == 1:
                msg = 'مطلب شما با موفقیت ارسال شد. <a href="%s">مشاهده</a>' %\
                    reverse('pin-item', args=[model.id])
                messages.add_message(request, messages.SUCCESS, msg)
            elif model.status == 0:
                msg = 'مطلب شما با موفقیت ارسال شد و بعد از تایید در سایت نمایش داده می شود '
                messages.add_message(request, messages.SUCCESS, msg)

            return HttpResponseRedirect('/pin/')
    else:
        form = PinForm()

    return render(request, 'pin/sendurl.html', {'form': form})


@login_required
@csrf_exempt
def a_sendurl(request):
    if request.method == "POST":
        url = request.POST['url']

        if url == '':
            return HttpResponse(0)

        images = get_images(url)
        if images == 0:
            return HttpResponse(0)

        return HttpResponse(json.dumps(images))
    else:
        return HttpResponse(0)


@login_required
def send(request):
    if request.method == "POST":
        post_values = request.POST.copy()
        # tags = post_values['tags']
        # post_values['tags'] = tags[tags.find("[") + 1:tags.find("]")]
        form = PinForm(post_values)
        if form.is_valid():
            model = form.save(commit=False)
            filename = model.image
            image_o = "%s/pin/temp/o/%s" % (MEDIA_ROOT, filename)
            image_on = "%s/pin/images/o/%s" % (MEDIA_ROOT, filename)

            copyfile(image_o, image_on)

            model.image = "pin/images/o/%s" % (filename)
            model.timestamp = time()
            model.user = request.user
            model.save()

            form.save_m2m()

            if model.status == 1:
                msg = 'مطلب شما با موفقیت ارسال شد. <a href="%s">مشاهده</a>' %\
                    reverse('pin-item', args=[model.id])
                messages.add_message(request, messages.SUCCESS, msg)
            elif model.status == 0:
                msg = 'مطلب شما با موفقیت ارسال شد و بعد از تایید در سایت نمایش داده می شود '
                messages.add_message(request, messages.SUCCESS, msg)

            return HttpResponseRedirect('/pin/')
    else:
        form = PinForm()

    category = Category.objects.all()

    if request.is_ajax():
        return render(request, 'pin/_send.html', {'form': form, 'category': category})
    else:
        return render(request, 'pin/send.html', {'form': form, 'category': category})


@login_required
def edit(request, post_id):
    try:
        post = Post.objects.get(pk=int(post_id))
        if not request.user.is_superuser:
            if post.user.id != request.user.id:
                return HttpResponseRedirect('/pin/')

        if request.method == "POST":
            post_values = request.POST.copy()
            # tags = post_values['tags']
            # post_values['tags'] = tags[tags.find("[") + 1:tags.find("]")]
            form = PinUpdateForm(post_values, instance=post)
            if form.is_valid():
                form.save()
                if request.is_ajax():
                    return HttpResponse('با موفقیت به روزرسانی شد.')
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
    ''' raw_data: if True, upfile is a HttpRequest object with raw post data
        as the file, rather than a Django UploadedFile from request.FILES '''
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
        # could not open the file most likely
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
                return HttpResponseBadRequest("AJAX request not valid")
        else:
            is_raw = False
            if len(request.FILES) == 1:
                upload = request.FILES.values()[0]
            else:
                raise Http404("Bad Upload")
            filename = upload.name

        filename = create_filename(filename)
        success = save_upload(upload, filename, is_raw)
        if success:
            image_o = "%s/pin/temp/o/%s" % (MEDIA_ROOT, filename)
            image_t = "%s/pin/temp/t/%s" % (MEDIA_ROOT, filename)

            pin_image.resize(image_o, image_t, 99)

        ret_json = {'success': success, 'file': filename}
        return HttpResponse(json.dumps(ret_json))

    return HttpResponseBadRequest("Bad request")


@login_required
def show_notify(request):
    Notif.objects.filter(owner=request.user.id, seen=False).update(set__seen=True)
    notif = Notif.objects.all().filter(owner=request.user.id).order_by('-date')[:20]
    nl = []
    for n in notif:
        anl = {}
        try:
            anl['po'] = Post.objects.only('image').get(pk=n.post)
        except Post.DoesNotExist:
            continue
        anl['id'] = n.post
        anl['type'] = n.type
        anl['actors'] = n.actors

        nl.append(anl)
    return render(request, 'pin2/notify.html', {'notif': nl})

@login_required
def notif_user(request):
    timestamp = get_request_timestamp(request)
    if timestamp:
        date = datetime.datetime.fromtimestamp(timestamp)
        notif = Notif.objects.filter(owner=request.user.id, date__lt=date)\
            .order_by('-date')[:20]
    else:
        notif = Notif.objects.filter(owner=request.user.id)\
            .order_by('-date')[:20]

    nl = []
    for n in notif:
        anl = {}
        try:
            anl['po'] = Post.objects.values('image').get(pk=n.post)['image']
        except Post.DoesNotExist:
            continue
        anl['id'] = n.post
        anl['type'] = n.type
        anl['actors'] = n.last_actors

        nl.append(anl)
        

    #for n in notif:
    #    print 'pois', n.po

    if request.is_ajax():
        return render(request, 'pin/_notif.html', {'notif': nl})
    else:
        return render(request, 'pin/notif_user.html', {'notif': nl})

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
        callBackUrl = 'http://127.0.0.1:800/%s' % reverse('pin-verify-payment')

        url = 'https://ir.zarinpal.com/pg/services/WebGate/wsdl'
        client = Client(url)
        desc = u'پرداخت سورتحساب'

        data = {'MerchantID': MERCHANT_ID,
                'Amount': 100,
                'Description': desc,
                'Email': "vchakoshy@gmail.com",
                'Mobile': "09195308965",
                'CallbackURL': callBackUrl}

        result = client.service.PaymentRequest(**data)
        print result

        if result['Status'] == 100:
            url = 'https://www.zarinpal.com/pg/StartPay/%s' % str(result['Authority'])
            return HttpResponseRedirect(url)
        else:
            messages.error(request, 'خطا هنگام وصل به سرور بانک')
            return HttpResponseRedirect(reverse('bill_view'))
    return render(request, 'pin2/inc_credit.html', {

    })


def verify_payment(request):

    Authority = request.GET.get('Authority', False)
    status = request.GET.get('Status', False)

    if Authority and status == 'OK':

        url = 'https://ir.zarinpal.com/pg/services/WebGate/wsdl'
        client = Client(url)
        data = {'MerchantID': MERCHANT_ID,
                'Amount': 100,
                'Authority': Authority}

        result = client.service.PaymentVerification(**data)

        if result['Status'] == 100:
            bill.trans_id = result['RefID']
            bill.pay_status = True
            bill.total_payed = bill.total_discount
            bill.save()
            messages.success(request, 'پرداخت با موفقیت انجام شد. کد رهگیری شما %s' % str(result['RefID']))
            return HttpResponseRedirect(reverse('bill_view', args=[bill.number]))
        else:
            messages.error(request, 'پرداخت نا موفق، در صورت کسر از حساب شما بانک مبلغ را برگشت خواهد داد.')
            return HttpResponseRedirect(reverse('profile'))

    else:
        return HttpResponseRedirect(reverse('profile'))