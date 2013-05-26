# coding: utf-8

import os
import time
import json
import urllib
import sys
from shutil import copyfile

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponseRedirect, HttpResponseBadRequest, Http404, HttpResponse
from django.shortcuts import render_to_response, get_object_or_404, render
from django.template.context import RequestContext
from django.views.decorators.csrf import csrf_exempt

import pin_image
from pin.crawler import get_images
from pin.forms import PinForm, PinUpdateForm, PinDirectForm
from pin.models import Post, Follow, Stream, Likes, Notify, Category
from pin.tools import create_filename

from user_profile.models import Profile
from taggit.models import Tag, TaggedItem
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.contenttypes.models import ContentType

from tastypie.models import ApiKey

MEDIA_ROOT = settings.MEDIA_ROOT

def home(request):
    
    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    
    if timestamp == 0:
        latest_items = Post.objects.filter(status=1).select_related().order_by('-timestamp')[:20]
    else:
        latest_items = Post.objects.filter(status=1).extra(where=['timestamp<%s'], params=[timestamp]).order_by('-timestamp')[:20]
    
    form = PinForm()
    
    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'pin/_items.html', {'latest_items': latest_items,'pin_form':form})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/home.html', {'latest_items': latest_items})

def popular(request):
    ROW_PER_PAGE = 20
    
    post_list = Post.objects.filter(status=1).select_related().order_by('-like')
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
    
    form = PinForm()
    
    if request.is_ajax():
        return render(request, 'pin/_items.html', 
                              {'latest_items': latest_items,'pin_form':form,'offset':latest_items.next_page_number})
        
    else:
        return render(request, 'pin/home.html', 
                              {'latest_items': latest_items, 'offset':latest_items.next_page_number})
    

def user(request, user_id):
    user = get_object_or_404(User, pk=user_id)

    profile, created = Profile.objects.get_or_create(user=user)
    if not profile.count_flag:
        profile.user_statics()

    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    
    if timestamp == 0:
        latest_items = Post.objects.filter(status=1).select_related().filter(user=user_id).order_by('-timestamp')[:20]
    else:
        latest_items = Post.objects.filter(user=user_id,status=1).extra(where=['timestamp<%s'], params=[timestamp]).order_by('-timestamp')[:20]
    
    form = PinForm()
    
    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'pin/_items.html', {'latest_items': latest_items,'pin_form':form})
        else:
            return HttpResponse(0)
    else:
        
        follow_status = Follow.objects.filter(follower=request.user.id,
            following=user.id).count()
        
        return render(request, 'pin/user.html', 
                              {'latest_items': latest_items, 'follow_status':follow_status,
                               'profile':profile,
                               'cur_user':user})

@login_required
def following(request):
    
    try:
        timestamp = int(request.GET.get('older', 0))
    except ValueError:
        timestamp = 0
    
    if timestamp == 0:
        stream = Stream.objects.filter(user=request.user).order_by('-date')[:20]
    else:
        stream = Stream.objects.filter(user=request.user).extra(where=['date<%s'], params=[timestamp]).order_by('-date')[:20]
    
    idis = []
    for p in stream:
        idis.append(int(p.post_id))
    
    latest_items = Post.objects.filter(id__in=idis,status=1).all().order_by('-id')
    
    #objects = dict([(int(obj.id), obj) for obj in latest_items])
    
    #sorted_objects = [objects[id] for id in idis]
    #sorted_objects=objects
    #for id in idis:
    #    sorted_objects.append(objects[id])

    sorted_objects=latest_items

    form = PinForm()
    
    if request.is_ajax():
        if latest_items.exists():
            return render(request, 'pin/_items.html', {'latest_items': sorted_objects,'pin_form':form})
        else:
            return HttpResponse(0)
    else:
        return render(request, 'pin/home.html', {'latest_items': sorted_objects})

@login_required
def follow(request, following, action):
    
    if int(following) == request.user.id:
        return HttpResponseRedirect(reverse('pin-home'))
    
    try:
        following = User.objects.get(pk=int(following))
        
        follow, created = Follow.objects.get_or_create(follower=request.user, following=following)
        
        if int(action) == 0:
            follow.delete()
            
            Stream.objects.filter(following=following, user=request.user).all().delete()
            
        else:
            posts = Post.objects.filter(user=following,status=1)[:100]
            
            with transaction.commit_on_success():
                for post in posts:
                    stream = Stream(post=post, user=request.user, date=post.timestamp, following=following)
                    stream.save()
        
        return HttpResponseRedirect(reverse('pin-user', args=[following.id]))
    except User.DoesNotExist:
        return HttpResponseRedirect(reverse('pin-user', args=[following.id]))

def item(request, item_id):
    
    item = get_object_or_404(Post.objects.select_related().filter(id=item_id,status=1)[:1])
    
    latest_items = Post.objects.filter(status=1).select_related().extra(where=['timestamp<%s'], params=[item.timestamp]).order_by('-timestamp')[:30]
    
    likes = Likes.objects.filter(post=item).all()
    
    follow_status = Follow.objects.filter(follower=request.user.id, following=item.user.id).count()
    
    if request.is_ajax():
        return render(request, 'pin/item_inner.html', 
                              {'item_inner': item, 'latest_items': latest_items, 'likes':likes, 'follow_status':follow_status})
    else:
        return render(request, 'pin/item.html', 
                              {'item_inner': item, 'latest_items': latest_items, 'likes':likes, 'follow_status':follow_status})

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
            
            #str = "%f" % time.time()
            #str = str.replace('.', '')
        
            #filename = "%s%s" % (str, os.path.splitext(filename)[1])
            filename = create_filename(filename)
            #filename = "%s%s" % (str, filename)
                        
            image_on = "%s/pin/images/o/%s" % ( MEDIA_ROOT, filename)
                                 
            urllib.urlretrieve(image_url, image_on)
            
            model.image = "pin/images/o/%s" % (filename)
            model.timestamp = time.time()
            model.user = request.user
            model.save()
            
            form.save_m2m()
            
            return HttpResponseRedirect('/pin/')
    else:
        form = PinForm()
            
    return render(request, 'pin/sendurl.html',{'form':form}) 

@csrf_exempt
def d_like(request):
    """
        Devices like android application can send request to like ap post
    """
    token = request.GET.get('token','')

    if not token:
        return HttpResponse('error in user validation')
    
    try:
        api = ApiKey.objects.get(key=token)
        user = api.user
    except ApiKey.DoesNotExist:
        return HttpResponse('error in user validation')
    if request.method == 'POST' and user.is_active:
        try:
            post_id = int(request.POST['post_id'])
        except ValueError:
            return HttpResponse('erro in post id')
        try:
            post = Post.objects.get(pk=post_id,status=1)
        except Post.DoesNotExist:
            return HttpResponse('post not found')

        like, created = Likes.objects.get_or_create(user=user, post=post)
        if created:
            post.like=post.like+1
            post.save()
            return HttpResponse('+1')
        elif like:
            like.delete()
            post.like=post.like-1
            post.save()
            return HttpResponse('-1')

    return HttpResponse('error in parameters')

@csrf_exempt
def d_send(request):
    token = request.GET.get('token','')
    
    if not token:
        return HttpResponse('error in user validate')
    
    try:
        api = ApiKey.objects.get(key=token)
        user = api.user
    except ApiKey.DoesNotExist:
        return HttpResponse('error in user validate')
    
    if request.method == 'POST' and user.is_active:
        form = PinDirectForm(request.POST, request.FILES)
        if form.is_valid():
            upload = request.FILES.values( )[ 0 ]
            filename = create_filename(upload.name)
            
            try:
                from io import FileIO, BufferedWriter
                with BufferedWriter( FileIO( "%s/pin/images/o/%s" % (MEDIA_ROOT, filename), "wb" ) ) as dest:
                    for c in upload.chunks( ):
                        dest.write( c )
                        
                    ## after upload we need to save model
                    model = Post()
                    model.image = "pin/images/o/%s" % (filename)
                    model.user = api.user
                    model.timestamp = time.time()
                    model.text = form.cleaned_data['description']
                    model.category_id = form.cleaned_data['category']
                    model.device = 2
                    model.save()
                    
                    return HttpResponse('success')
            except IOError:
                # could not open the file most likely
                return HttpResponse('error')
            
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
        post_values['tags']=tags[tags.find("[")+1:tags.find("]")]
        form = PinForm(post_values)
        if form.is_valid():
            model = form.save(commit=False)
            
            filename= model.image
            
            image_o = "%s/pin/temp/o/%s" % ( MEDIA_ROOT,filename)
            
            image_on = "%s/pin/images/o/%s" % ( MEDIA_ROOT, filename)
            
            copyfile(image_o, image_on)
            
            model.image = "pin/images/o/%s" % (filename)
            model.timestamp = time.time()
            model.user = request.user
            model.save()
            
            form.save_m2m()
            
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
        if post.user.id != request.user.id:
            return HttpResponseRedirect('/pin/')

        if request.method == "POST":
            post_values = request.POST.copy()
            tags = post_values['tags']
            post_values['tags']=tags[tags.find("[")+1:tags.find("]")]
            form = PinUpdateForm(post_values, instance=post)
            if form.is_valid():
                model = form.save(commit=False)
                
                model.save()
                
                form.save_m2m()
                
                return HttpResponse('با موفقیت به روزرسانی شد.')
        else:
            form = PinUpdateForm(instance=post)
        
        if request.is_ajax():
            return render_to_response('pin/_edit.html',{'form': form, 'post':post}, context_instance=RequestContext(request))
        else:
            return render_to_response('pin/edit.html',{'form': form, 'post':post}, context_instance=RequestContext(request))
    except Post.DoesNotExist:
        return HttpResponseRedirect('/pin/')


def save_upload( uploaded, filename, raw_data ):
    ''' raw_data: if True, upfile is a HttpRequest object with raw post data
        as the file, rather than a Django UploadedFile from request.FILES '''
    try:
        from io import FileIO, BufferedWriter
        with BufferedWriter( FileIO( "%s/pin/temp/o/%s" % (MEDIA_ROOT, filename), "wb" ) ) as dest:

            if raw_data:
                foo = uploaded.read( 1024 )
                while foo:
                    dest.write( foo )
                    foo = uploaded.read( 1024 ) 
            # if not raw, it was a form upload so read in the normal Django chunks fashion
            else:
                for c in uploaded.chunks( ):
                    dest.write( c )
            return True
    except IOError:
        # could not open the file most likely
        return False

@csrf_exempt
def upload(request):
    if request.method == "POST":
        if request.is_ajax( ):
            upload = request
            is_raw = True
            try:
                filename = request.GET[ 'qqfile' ]
            except KeyError: 
                return HttpResponseBadRequest( "AJAX request not valid" )
        else:
            is_raw = False
            if len( request.FILES ) == 1:
                upload = request.FILES.values( )[ 0 ]
            else:
                raise Http404( "Bad Upload" )
            filename = upload.name
        
        #str = "%f" % time.time()
        #str = str.replace('.', '')
        
        #filename = "%s%s" % (str, os.path.splitext(filename)[1])
        filename = create_filename(filename)
        
        # save the file
        success = save_upload( upload, filename, is_raw )
        
        if success:
            image_o = "%s/pin/temp/o/%s" % (MEDIA_ROOT, filename)
            image_t = "%s/pin/temp/t/%s" % (MEDIA_ROOT, filename)
            
            pin_image.resize(image_o, image_t, 99)
            
        ret_json = {'success':success,'file':filename}
        return HttpResponse( json.dumps( ret_json ) )

def comment_posted(request):
    if request.GET['c']:
        comment_id = request.GET['c'] #B
        comment = Comment.objects.get( pk=comment_id )
        entry = Post.objects.get(id=comment.object_pk,status=1) #C
        if entry:
            return HttpResponseRedirect( entry.get_absolute_url() ) #D
    return HttpResponseRedirect( "/" )     

@login_required
def delete(request, item_id):
    try:
        post = Post.objects.get(pk=item_id)
        if post.user == request.user or request.user.is_superuser:
            likes = Likes.objects.filter(post_id=post.id)
            for like in likes:
                like.delete()
                
            post.delete()
            return HttpResponse('1')
            
    except Post.DoesNotExist:
        return HttpResponse('0')
    
    return HttpResponse('0')

@login_required
def like(request, item_id):

    try:
        post = Post.objects.get(pk=item_id,status=1)
        current_like = post.like
        
        liked = Likes.objects.filter(user=request.user, post=post).count()
        
        user_act = 0
        
        if not liked:
            like = Likes()
            like.user = request.user
            like.post = post
            like.save()
            
            current_like = current_like+1
            user_act = 1
            
        else:
            current_like = current_like-1
            Likes.objects.filter(user=request.user,post=post).delete()
            user_act = -1
        
        Post.objects.filter(id=item_id).update(like=current_like)
        
        profile = Profile.objects.get(user=post.user)
        profile.save()
        
        if request.is_ajax():
            
            data = [{'likes': current_like, 'user_act':user_act}]
                       
            return HttpResponse(json.dumps(data))
        else:
            return HttpResponseRedirect(reverse('pin-item', args=[post.id]))
            
    except Post.DoesNotExist:
        return HttpResponseRedirect('/')

def show_notify(request):
    Notify.objects.filter(user_id=request.user.id, seen=False).update(seen=True)
    notif = Notify.objects.all().filter(user_id=request.user.id).order_by('-id')[:20]
    return render_to_response('pin/notify.html',{'notif':notif})

def tag_complete(request):
    q = request.GET['q']
    data = []
    for x in range(10):
        data.append("%s %s" % (q, x))
    return HttpResponse(json.dumps(data))

def delneveshte(request):
    return render_to_response('pin/delneveshte2.html',context_instance=RequestContext(request))

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
        
    latest_items = Post.objects.filter(id__in=s,status=1).all()
    
    form = PinForm()
    
    if request.is_ajax():
        if latest_items.exists():
            return render_to_response('pin/_items.html', 
                              {'latest_items': latest_items,'pin_form':form, 'offset':tag_items.next_page_number},
                              context_instance=RequestContext(request))
        else:
            return HttpResponse(0)
    else:
        return render_to_response('pin/tag.html', 
                              {'latest_items': latest_items, 'tag': tag,'offset':tag_items.next_page_number},
                              context_instance=RequestContext(request))
    
    #return render_to_response('pin/home.html',context_instance=RequestContext(request))

def trust_user(request, user_id):
    if request.user.is_superuser:
        profile = Profile.objects.get(user_id=user_id)
        profile.trusted = 1
        profile.trusted_by = request.user
        profile.save()

    return HttpResponseRedirect('/pin/user/'+user_id)

