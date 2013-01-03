# Create your views here.
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.http import HttpResponseRedirect

from user_profile.forms import ProfileForm
from user_profile.models import Profile
from django.contrib.auth.decorators import login_required

@login_required
def change(request):
    profile, create = Profile.objects.get_or_create(user=request.user)
    
    #profile=Profile.objects.filter(user=request.user).get()
    if request.method== "POST":
        form=ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            profile= form.save(commit=False)
            profile.save()
        
            return HttpResponseRedirect('/pin/user/%d' % request.user.id)
    else:
        form = ProfileForm(instance=profile)
    return render_to_response('change.html',{'form':form},context_instance=RequestContext(request))
