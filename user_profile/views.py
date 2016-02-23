# Create your views here.

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import ugettext_lazy as _

from user_profile.forms import ProfileForm
from user_profile.models import Profile

from tastypie.models import ApiKey


@user_passes_test(lambda u: u.is_active, login_url='/pin/you_are_deactive/')
@login_required
def change(request):
    profile, create = Profile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/pin/user/%d' % request.user.id)
    else:
        form = ProfileForm(instance=profile)
        for f in form:
            print f.name

        if request.is_ajax():
            return render(request, '__change.html', {'form': form})
    return render(request, 'change.html', {'form': form})


@csrf_exempt
def d_change(request):
    token = request.GET.get('token', '')

    if not token:
        return HttpResponse(_('There is not token'))
    try:
        api = ApiKey.objects.get(key=token)
        user = api.user
    except ApiKey.DoesNotExist:
        return HttpResponse(_('error in user validation'))

    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == "POST":
        if not user.is_active:
            return HttpResponse(_('user is inactive'))
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return HttpResponse(_('profile has saved'))
        else:
            return HttpResponse(_('form not valid'))
    else:
        return HttpResponse(_('request method is not POST'))

    return HttpResponse(_('error in data'))
