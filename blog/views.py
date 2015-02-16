from operator import itemgetter
from django.shortcuts import render
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from datetime import datetime

from models import BlogPost, Comment
from forms import PostForm, CommentForm

def get_tags():
    tag_freqs = BlogPost.objects.item_frequencies('tags', normalize=True)
    print tag_freqs

    top_tags = sorted(tag_freqs.items(), key=itemgetter(1), reverse=True)[:10]
    tags = [t[0].replace(' ', "_") for t in top_tags]
    return tags

def home(request):
    posts = BlogPost.objects.order_by('-id')
    
    return render(request, 'blog/index.html', {
        'posts': posts,
        'top_tags': get_tags(),
    })

def tag(request, tag_name):
    posts = BlogPost.objects.filter(tags=tag_name)
    
    return render(request, 'blog/index.html', {
        'posts': posts,
        'top_tags': get_tags(),
    })

def admin(request):
    posts = BlogPost.objects.order_by('-id')
    return render(request, 'blog/admin.html', {
        'posts': posts
    })

def submit(request):
    if request.method == "POST":
        print request.POST
        form = PostForm(request.POST)
        if form.is_valid():
            tags = form.cleaned_data['tags'].split(',')
            tags = [t.replace(' ', '_') for t in tags]
            title = form.cleaned_data['title']
            abstract = form.cleaned_data['abstract']
            text = form.cleaned_data['text']
            ct = datetime.now()
            BlogPost.objects.create(title=title, text=text, abstract=abstract,  tags= tags, create_time=ct, user=request.user.id)

            return HttpResponseRedirect(reverse('blog-admin'))
    else:
        form = PostForm()
    return render(request, 'blog/submit.html', {
        'form': form,
    })

def edit(request, id):
    p = BlogPost.objects.get(id=id)
    if request.method == "POST":
        print request.POST
        form = PostForm(request.POST)
        if form.is_valid():
            p.tags = form.cleaned_data['tags'].split(',')
            p.tags = [t.replace(' ', '_') for t in p.tags]
            p.title = form.cleaned_data['title']
            p.abstract = form.cleaned_data['abstract']
            p.text = form.cleaned_data['text']
            p.user = request.user.id
            p.save()
            return HttpResponseRedirect(reverse('blog-admin'))
    else:
        p = BlogPost.objects.get(id=id)
        d = {
            'title': p.title,
            'abstract': p.abstract,
            'text': p.text,
            'tags': ",".join([t for t in p.tags])
        }

        form = PostForm(d)
    return render(request, 'blog/submit.html', {
        'form': form,
    })

def view_post(request, id):
    post = BlogPost.objects.get(id=id)

    # print request.method, request.user.is_authenticated()
    if request.method == "POST" and request.user.is_authenticated():
        form = CommentForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            ct = datetime.now()
            c = Comment(content=text, create_time=ct, user=request.user.id)
            post.update(add_to_set__comments=c)

            return HttpResponseRedirect(reverse('blog-view-post', args=[post.id]))
    else:
        form = CommentForm()

    return render(request, 'blog/view_post.html', {
        'post': post,
        'form': form
    })