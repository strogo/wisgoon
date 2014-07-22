# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test

from user_profile.forms import ProfileForm
from user_profile.models import Profile

from tastypie.models import ApiKey

@user_passes_test(lambda u: u.is_active, login_url='/pin/you_are_deactive/')
@login_required
def change(request):
    profile, create = Profile.objects.get_or_create(user=request.user)
    
    #profile=Profile.objects.filter(user=request.user).get()
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
        
            return HttpResponseRedirect('/pin/user/%d' % request.user.id)
    else:
        form = ProfileForm(instance=profile)
    return render_to_response('change.html',{'form':form},context_instance=RequestContext(request))

@csrf_exempt
def d_change(request):
    token = request.GET.get('token','')

    if not token:
        return HttpResponse('error in user validation')
    
    try:
        api = ApiKey.objects.get(key=token)
        user = api.user
    except ApiKey.DoesNotExist:
        return HttpResponse('error in user validation')

    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        if not user.is_active:
            return HttpResponse('user not active')
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.save()
            
            return HttpResponse('profile saved')
        else:
            return HttpResponse('form not valid')
    else:
        return HttpResponse('request method != POST')

    return HttpResponse('error in data')












