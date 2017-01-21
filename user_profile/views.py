# Create your views here.

from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, UnreadablePostError
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages
from django.core.urlresolvers import reverse

from user_profile.forms import ProfileForm
from user_profile.models import Profile

from pin.api6.tools import is_system_writable, update_follower_following
from pin.decorators import system_writable
from pin.models import Log
from pin.tools import get_user_ip

from tastypie.models import ApiKey


@user_passes_test(lambda u: u.is_active, login_url='/pin/you_are_deactive/')
@login_required
@system_writable
def change(request):
    if is_system_writable() is False:
        msg = _("Website update in progress.")
        if request.is_ajax():
            return HttpResponse(msg)
        else:
            messages.error(request, msg)
            return HttpResponseRedirect(
                reverse('pin-absuser',
                        args=[request.user.username])
            )

    current_user = request.user
    current_user_id = current_user.id
    profile, create = Profile.objects.get_or_create(user=current_user)
    if request.method == "POST":
        try:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
        except UnreadablePostError:
            return HttpResponse(_('Error sending the image.'))

        if form.is_valid():
            p = form.save()
            update_follower_following(profile, current_user_id)
            Log.update_profile(actor=current_user,
                               user_id=current_user_id,
                               text=_("update profile"),
                               image=p.avatar,
                               ip_address=get_user_ip(request=request))
            return HttpResponseRedirect('/pin/user/%d' % current_user_id)
    else:
        form = ProfileForm(instance=profile)
        if request.is_ajax():
            return render(request, '__change.html', {'form': form})
    return render(request, 'change.html', {'form': form})


@csrf_exempt
@system_writable
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
        try:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
        except UnreadablePostError:
            return HttpResponse(_('Error sending the image.'))

        if form.is_valid():
            form.save()
            return HttpResponse(_('profile has saved'))
        else:
            return HttpResponse(_('form not valid'))
    else:
        return HttpResponse(_('request method is not POST'))

    return HttpResponse(_('error in data'))
