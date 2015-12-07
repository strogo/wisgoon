from django.shortcuts import render
from tastypie.models import ApiKey
from daddy_avatar.templatetags.daddy_avatar import get_avatar


def home(request):
    if request.user.is_authenticated():
        api_key, created = ApiKey.objects.get_or_create(user=request.user)
        request.user.token = str(api_key.key)
        request.user.avatar = get_avatar(user=request.user)
    return render(request, 'angular/home.html')

def latest(request):
    return render(request, 'angular/latest.html')

def post(request):
    return render(request, 'angular/post.html')

def catPage(request):
    return render(request, 'angular/cat-page.html')

def search(request):
    return render(request, 'angular/search.html')

def EditorPosts(request):
    return render(request, 'angular/editor-posts.html')

def login(request):
    return render(request, 'angular/login.html')

def register(request):
    return render(request, 'angular/register.html')

def sendPost(request):
    return render(request, 'angular/send-post.html')

def profile(request):
    return render(request, 'angular/profile.html')

def editProfile(request):
    return render(request, 'angular/edit-profile.html')

def likedPost(request):
    return render(request, 'angular/liked-post.html')

def friendsPost(request):
    return render(request, 'angular/friends-post.html')

def notifs(request):
    return render(request, 'angular/all-notifs.html')

def editPost(request):
    return render(request, 'angular/edit-post.html')

def followingsList(request):
    return render(request, 'angular/followings-list.html')

def followersList(request):
    return render(request, 'angular/followers-list.html')
