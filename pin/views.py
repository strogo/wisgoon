# coding: utf-8

from time import time, mktime
import json
import urllib
import datetime
from shutil import copyfile

from httplib import HTTPSConnection
from BeautifulSoup import BeautifulStoneSoup

from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.db.models import Sum, F
from django.http import HttpResponseRedirect, HttpResponseBadRequest,\
    Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt

import pin_image
from pin.crawler import get_images
from pin.forms import PinForm, PinUpdateForm
from pin.models import Post, Follow, Stream, Likes, Notif, Category,\
    Notif_actors, Comments, Report, Comments_score
from pin.tools import create_filename

from user_profile.models import Profile
from taggit.models import Tag, TaggedItem

MEDIA_ROOT = settings.MEDIA_ROOT
REPORT_TYPE = settings.REPORT_TYPE


def get_request_timestamp(request):
    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    return timestamp


def home(request):
    timestamp = get_request_timestamp(request)

    if timestamp == 0:
        latest_items = Post.accepted.filter(show_in_default=1)\
            .order_by('-is_ads', '-timestamp')[:20]
    else:
        latest_items = Post.accepted.filter(show_in_default=1)\
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
        return render(request, 'pin/home.html', {'latest_items': latest_items})


def user_like(request, user_id):
    user_id = int(user_id)
    ROW_PER_PAGE = 20
    likes_list = []
    
    likes = Likes.objects.values_list('post_id', flat=True)\
        .filter(user_id=user_id).order_by('-id')

    paginator = Paginator(likes, ROW_PER_PAGE)

    try:
        offset = int(request.GET.get('older', 1))
    except ValueError:
        offset = 1

    try:
        likes = paginator.page(offset)
    except PageNotAnInteger:
        likes = paginator.page(1)
    except EmptyPage:
        return HttpResponse(0)

    if likes.has_next() is False:
        likes.next_page_number = -1

    for l in likes:
        likes_list.append(int(l))
    
    latest_items = Post.accepted.filter(id__in=likes_list)

    if request.is_ajax():
        if latest_items.exists():
            return render(request,
                          'pin/_items.html',
                          {'latest_items': latest_items,
                           'offset': likes.next_page_number})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/mylike.html', 
            {'latest_items': latest_items,
             'offset': likes.next_page_number,
             'user_id': user_id,
            })


def latest(request):
    timestamp = get_request_timestamp(request)

    if timestamp == 0:
        latest_items = Post.accepted\
            .order_by('-is_ads', '-timestamp')[:20]
    else:
        latest_items = Post.accepted\
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
        return render(request, 'pin/home.html', {'latest_items': latest_items})


def category(request, cat_id):
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


def popular(request, interval=""):
    ROW_PER_PAGE = 20

    if interval and interval in ['month', 'lastday', 'lasteigth', 'lastweek']:
        if interval == 'month':
            data_from = datetime.datetime.now() - datetime.timedelta(days=30)
        elif interval == 'lastday':
            data_from = datetime.datetime.now() - datetime.timedelta(days=1)
        elif interval == 'lastweek':
            data_from = datetime.datetime.now() - datetime.timedelta(days=7)
        elif interval == 'lasteigth':
            data_from = datetime.datetime.now() - datetime.timedelta(hours=8)

        start_from = mktime(data_from.timetuple())
        post_list = Post.objects.filter(status=1)\
            .extra(where=['timestamp>%s'], params=[start_from])\
            .order_by('-cnt_like')

    else:
        post_list = Post.objects.filter(status=1)\
            .order_by('-cnt_like')
    paginator = Paginator(post_list, ROW_PER_PAGE)

    try:
        offset = int(request.GET.get('older', 1))
    except ValueError:
        offset = 1

    try:
        latest_items = paginator.page(offset)
    except PageNotAnInteger:
        latest_items = paginator.page(1)
    except EmptyPage:
        return HttpResponse(0)

    if request.is_ajax():
        return render(request, 'pin/_items.html',
                      {'latest_items': latest_items,
                      'offset': latest_items.next_page_number})

    else:
        return render(request, 'pin/home.html',
                      {'latest_items': latest_items,
                      'offset': latest_items.next_page_number})


def topuser(request):
    top_user = Profile.objects.all().order_by('-score')[:152]

    return render(request, 'pin/topuser.html', {'top_user': top_user})


def topgroupuser(request):
    cats = Category.objects.all()
    for cat in cats:
        cat.tops = Post.objects.values('user_id')\
            .filter(category_id=cat.id)\
            .annotate(sum_like=Sum('cnt_like'))\
            .order_by('-sum_like')[:4]
        for ut in cat.tops:
            ut['user'] = User.objects.get(pk=ut['user_id'])

    return render(request, 'pin/topgroupuser.html', {'cats': cats})


def user(request, user_id, user_name=None):
    user = get_object_or_404(User, pk=user_id)

    profile, created = Profile.objects.get_or_create(user=user)
    if not profile.count_flag:
        profile.user_statics()

    timestamp = get_request_timestamp(request)

    if request.user == user:
        if timestamp == 0:
            latest_items = Post.objects.filter(user=user_id)\
                .order_by('-timestamp')[:20]
        else:
            latest_items = Post.objects.filter(user=user_id)\
                .extra(where=['timestamp<%s'], params=[timestamp])\
                .order_by('-timestamp')[:20]

    else:
        if timestamp == 0:
            latest_items = Post.objects.filter(status=1, user=user_id)\
                .order_by('-timestamp')[:20]
        else:
            latest_items = Post.objects.filter(user=user_id, status=1)\
                .extra(where=['timestamp<%s'], params=[timestamp])\
                .order_by('-timestamp')[:20]

    form = PinForm()

    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'pin/_items.html',
                          {'latest_items': latest_items, 'pin_form': form})
        else:
            return HttpResponse(0)
    else:

        follow_status = Follow.objects\
            .filter(follower=request.user.id, following=user.id).count()

        return render(request, 'pin/user.html',
                      {'latest_items': latest_items,
                      'follow_status': follow_status,
                      'profile': profile,
                      'cur_user': user})


@login_required
def following(request):
    timestamp = get_request_timestamp(request)

    if timestamp == 0:
        stream = Stream.objects.filter(user=request.user)\
            .order_by('-date')[:20]
    else:
        stream = Stream.objects.filter(user=request.user)\
            .extra(where=['date<%s'], params=[timestamp])\
            .order_by('-date')[:20]

    idis = []
    for p in stream:
        idis.append(int(p.post_id))

    latest_items = Post.objects.filter(id__in=idis, status=1)\
        .all().order_by('-id')

    sorted_objects = latest_items

    if request.is_ajax():
        if latest_items.exists():
            return render(request,
                          'pin/_items.html',
                          {'latest_items': sorted_objects})
        else:
            return HttpResponse(0)
    else:
        return render(request,
                      'pin/home.html',
                      {'latest_items': sorted_objects})


@login_required
def follow(request, following, action):
    if int(following) == request.user.id:
        return HttpResponseRedirect(reverse('pin-home'))

    try:
        following = User.objects.get(pk=int(following))

        follow, created = Follow.objects.get_or_create(follower=request.user,
                                                       following=following)

        if int(action) == 0:
            follow.delete()
            Stream.objects.filter(following=following, user=request.user)\
                .all().delete()
        else:
            posts = Post.objects.filter(user=following, status=1)[:100]
            with transaction.commit_on_success():
                for post in posts:
                    stream = Stream(post=post,
                                    user=request.user,
                                    date=post.timestamp,
                                    following=following)
                    stream.save()
        return HttpResponseRedirect(reverse('pin-user', args=[following.id]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('pin-user', args=[following.id]))


def item(request, item_id):
    post = get_object_or_404(Post.objects.select_related().filter(id=item_id, status=1)[:1])
    Post.objects.filter(id=item_id).update(view=F('view') + 1)
    
    post.tag = post.tags.all()

    if request.user.is_superuser and request.GET.get('ip', None):
        post.comments = Comments.objects.filter(object_pk=post)
        post.likes = Likes.objects.filter(post=post).order_by('ip')
    else:
        post.comments = Comments.objects.filter(object_pk=post, is_public=True)
        post.likes = Likes.objects.filter(post=post)
    
    try:
        post.prev = Post.objects.filter(status=1)\
            .extra(where=['id<%s'], params=[post.id]).order_by('-id')[:1][0]
        post.next = Post.objects.filter(status=1)\
            .extra(where=['id>%s'], params=[post.id]).order_by('id')[:1][0]
    except:
        pass
    
    follow_status = Follow.objects.filter(follower=request.user.id, following=post.user.id).count()
    
    if request.is_ajax():
        return render(request, 'pin/item_inner.html',
                      {'post': post, 'follow_status': follow_status})
    else:
        return render(request, 'pin/item.html',
                      {'post': post, 'follow_status': follow_status})

@login_required
def sendurl(request):
    if request.method == "POST":
        post_values = request.POST.copy()
        tags = post_values['tags']
        post_values['tags']=tags[tags.find("[")+1:tags.find("]")]
        form = PinForm(post_values)
        if form.is_valid():
            model = form.save(commit=False)
            
            image_url= model.image
            
            filename = image_url.split('/')[-1]

            filename = create_filename(filename)
                        
            image_on = "%s/pin/images/o/%s" % ( MEDIA_ROOT, filename)
                                 
            urllib.urlretrieve(image_url, image_on)
            
            model.image = "pin/images/o/%s" % (filename)
            model.timestamp = time()
            model.user = request.user
            model.save()
            
            form.save_m2m()

            if model.status == 1:
                msg = 'مطلب شما با موفقیت ارسال شد. <a href="%s">مشاهده</a>' % reverse('pin-item', args=[model.id])
                messages.add_message(request, messages.SUCCESS, msg)
            elif model.status == 0:
                msg = 'مطلب شما با موفقیت ارسال شد و بعد از تایید در سایت نمایش داده می شود '
                messages.add_message(request, messages.SUCCESS, msg)

            
            return HttpResponseRedirect('/pin/')
    else:
        form = PinForm()
            
    return render(request, 'pin/sendurl.html',{'form':form}) 

            
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
        tags = post_values['tags']
        post_values['tags'] = tags[tags.find("[") + 1:tags.find("]")]
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
                msg = 'مطلب شما با موفقیت ارسال شد. <a href="%s">مشاهده</a>' % reverse('pin-item', args=[model.id])
                messages.add_message(request, messages.SUCCESS, msg)
            elif model.status == 0:
                msg = 'مطلب شما با موفقیت ارسال شد و بعد از تایید در سایت نمایش داده می شود '
                messages.add_message(request, messages.SUCCESS, msg)
            
            return HttpResponseRedirect('/pin/')
    else:
        form = PinForm()
    
    category = Category.objects.all()
        
    if request.is_ajax():
        return render(request, 'pin/_send.html',{'form': form,'category': category})
    else:
        return render(request, 'pin/send.html',{'form': form, 'category': category})


@login_required
def edit(request, post_id):
    try:
        post = Post.objects.get(pk=int(post_id))
        if not request.user.is_superuser:
            if post.user.id != request.user.id:
                return HttpResponseRedirect('/pin/')

        if request.method == "POST":
            post_values = request.POST.copy()
            tags = post_values['tags']
            post_values['tags'] = tags[tags.find("[") + 1:tags.find("]")]
            form = PinUpdateForm(post_values, instance=post)
            if form.is_valid():
                model = form.save(commit=False)
                
                model.save()
                
                form.save_m2m()
                
                return HttpResponse('با موفقیت به روزرسانی شد.')
        else:
            form = PinUpdateForm(instance=post)
        
        if request.is_ajax():
            return render(request, 'pin/_edit.html', {'form': form, 'post': post})
        else:
            return render(request, 'pin/edit.html', {'form': form, 'post': post})
    except Post.DoesNotExist:
        return HttpResponseRedirect('/pin/')


def save_upload(uploaded, filename, raw_data ):
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
            
        ret_json = {'success': success,'file': filename}
        return HttpResponse(json.dumps(ret_json))


@login_required
def delete(request, item_id):
    try:
        post = Post.objects.get(pk=item_id)
        if post.user == request.user or request.user.is_superuser:
            post.delete()
            return HttpResponse('1')
            
    except Post.DoesNotExist:
        return HttpResponse('0')
    
    return HttpResponse('0')


@login_required
def like(request, item_id):
    try:
        post = Post.objects.get(pk=item_id, status=1)
        current_like = post.cnt_likes()

        try:
            liked = Likes.objects.get(user=request.user, post=post)
            created = False
        except Likes.DoesNotExist:
            liked = Likes.objects.create(user=request.user, post=post)
            created = True

        #liked, created = Likes.objects.get_or_create()

        if created:
            current_like = current_like + 1
            user_act = 1
            
            liked.ip = request.META.get("REMOTE_ADDR", '127.0.0.1')
            liked.save()
        elif liked:
            current_like = current_like - 1
            Likes.objects.get(user=request.user, post=post).delete()
            user_act = -1
        
        #Post.objects.filter(id=item_id).update(like=current_like)
        
        try:
            profile = Profile.objects.get(user=post.user)
            profile.save()
        except Profile.DoesNotExist:
            pass
        
        if request.is_ajax():
            data = [{'likes': current_like, 'user_act':user_act}]
            return HttpResponse(json.dumps(data))
        else:
            return HttpResponseRedirect(reverse('pin-item', args=[post.id]))
            
    except Post.DoesNotExist:
        return HttpResponseRedirect('/')


@login_required
def notif_user(request):
    timestamp = get_request_timestamp(request)
    if timestamp:
        date = datetime.datetime.fromtimestamp(timestamp)
        notif = Notif.objects.filter(user_id=request.user.id, date__lt=date).order_by('-date')[:20]
    else:
        notif = Notif.objects.filter(user_id=request.user.id).order_by('-date')[:20]

    for n in notif:
        n.actors = Notif_actors.objects.filter(notif=n).order_by('-id')[:20]

    if request.is_ajax():
        return render(request, 'pin/_notif.html', {'notif':notif})
    else:
        return render(request, 'pin/notif_user.html', {'notif':notif})


def show_notify(request):
    Notif.objects.filter(user_id=request.user.id, seen=False).update(seen=True)
    notif = Notif.objects.all().filter(user_id=request.user.id).order_by('-date')[:20]
    for n in notif:
        n.actors = Notif_actors.objects.filter(notif=n)
    return render(request, 'pin/notify.html',{'notif': notif})


def tag(request, keyword):
    ROW_PER_PAGE = 20
    
    tag = get_object_or_404(Tag, slug=keyword)
    content_type = ContentType.objects.get_for_model(Post)
    tag_items = TaggedItem.objects.filter(tag_id=tag.id, content_type=content_type)
    
    paginator = Paginator(tag_items, ROW_PER_PAGE)
    
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
    return render(request, 'pin/policy.html')


@csrf_exempt
@login_required
@user_passes_test(lambda u: u.is_active, login_url='/pin/you_are_deactive/')
def send_comment(request):
    if request.method == 'POST':
        text = request.POST.get('text', None)
        post = request.POST.get('post', None)
        if text and post:
            post = get_object_or_404(Post, pk=post)
            Comments.objects.create(object_pk=post,
                                    comment=text,
                                    user=request.user,
                                    ip_address=request.META.get('REMOTE_ADDR', None))

            return HttpResponseRedirect(reverse('pin-item', args=[post.id]))

    return HttpResponse('error')


def you_are_deactive(request):
    return render(request, 'pin/you_are_deactive.html')


@login_required
def comment_delete(request, id):
    comment = get_object_or_404(Comments, pk=id)
    post_id = comment.object_pk.id

    if not request.user.is_superuser:
        if comment.user != request.user:
            return HttpResponseRedirect(reverse('pin-item', args=[post_id]))

    comment.delete()

    return HttpResponseRedirect(reverse('pin-item', args=[post_id]))


@login_required
def comment_approve(request, id):
    if not request.user.is_superuser:
        return HttpResponse('error in authentication')

    comment = get_object_or_404(Comments, pk=id)
    comment.is_public = True
    comment.save()

    return HttpResponseRedirect(reverse('pin-item', args=[comment.object_pk.id]))


@login_required
def comment_unapprove(request, id):
    if not request.user.is_superuser:
        return HttpResponse('error in authentication')

    comment = get_object_or_404(Comments, pk=id)
    comment.is_public = False
    comment.save()

    return HttpResponseRedirect(reverse('pin-item', args=[comment.object_pk.id]))


@login_required
def comment_score(request, comment_id, score):
    score = int(score)
    scores = [1, 0]
    if score not in scores:
        return HttpResponse('error in scores')
    
    if score == 0:
        score = -1

    try:
        comment = Comments.objects.get(pk=comment_id)
        comment_score, created = Comments_score.objects.get_or_create(user=request.user, comment=comment)
        if score != comment_score.score:
            comment_score.score = score
            comment_score.save()
        
        sum_score = Comments_score.objects.filter(comment=comment).aggregate(Sum('score'))
        comment.score = sum_score['score__sum']
        comment.save()
        return HttpResponse(sum_score['score__sum'])

    except Comments.DoesNotExist:
        return HttpResponseRedirect('/')


@login_required
def report(request, pin_id):
    ### remove report if needed
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
        data = [{'status': status, 'msg':msg}]
        return HttpResponse(json.dumps(data))
    else:
        return HttpResponseRedirect(reverse('pin-item', args=[post.id]))


@login_required
def goto_index(request, item_id, status):
    if not request.user.is_superuser:
        return HttpResponseRedirect('/')

    if int(status) == 1:
        Post.objects.filter(pk=item_id).update(show_in_default=True)
        data = [{'status':1, 'url':reverse('pin-item-goto-index', args=[item_id, 0])}]
        return HttpResponse(json.dumps(data))
    else:
        Post.objects.filter(pk=item_id).update(show_in_default=False)
        data = [{'status':0, 'url':reverse('pin-item-goto-index', args=[item_id, 1])}]
        return HttpResponse(json.dumps(data))
    

def send_mail(request):
    from django.core.mail import EmailMultiAlternatives

    subject, from_email, to = 'hello', 'info@wisgoon.com', 'vchakoshy@gmail.com'
    text_content = 'shoma yek payame jadid darid.'
    html_content = '<p>This is an <strong>important</strong> message.</p>'
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

    return HttpResponse('done')








TOKEN_VAR = 'contact_token'
TOKEN_IN_GET = 'token'
def gdata_required(f):
    """
    Authenticate against Google GData service
    """
    def wrap(request, *args, **kwargs):
        if TOKEN_IN_GET not in request.GET and TOKEN_VAR not in request.session:
            # no token at all, request one-time-token
            # next: where to redirect
            # scope: what service you want to get access to
            return HttpResponseRedirect("https://www.google.com/accounts/AuthSubRequest?next=http://127.0.0.1:8000/pin/test_page&scope=https://www.google.com/m8/feeds&session=1")
        elif TOKEN_VAR not in request.session and TOKEN_IN_GET in request.GET:
            # request session token using one-time-token
            conn = HTTPSConnection("www.google.com")
            conn.putrequest('GET', '/accounts/AuthSubSessionToken')
            conn.putheader('Authorization', 'AuthSub token="%s"' % request.GET[TOKEN_IN_GET])
            conn.endheaders()
            conn.send(' ')
            r = conn.getresponse()
            if str(r.status) == '200':
                token = r.read()
                token = token.split('=')[1]
                token = token.replace('', '')
                request.session[TOKEN_VAR] = token
        return f(request, *args, **kwargs)
    wrap.__doc__=f.__doc__
    wrap.__name__=f.__name__
    return wrap

@gdata_required
def test_page1(request):
    """
    Simple example - list google docs documents
    """
    if TOKEN_VAR in request.session:
        con = HTTPSConnection("www.google.com")
        con.putrequest('GET', '/m8/feeds/contacts/vchakoshy@gmail.com/full')
        con.putheader('Authorization', 'AuthSub token="%s"' % request.session[TOKEN_VAR])
        con.endheaders()
        con.send('')
        r2 = con.getresponse()
        dane = r2.read()
        soup = BeautifulStoneSoup(dane)
        dane = soup.prettify()
        return render_to_response('pin/a.html', {'dane':dane}, context_instance=RequestContext(request))
    else:
        return render_to_response('pin/a.html', {'dane':'bad bad'}, context_instance=RequestContext(request))
