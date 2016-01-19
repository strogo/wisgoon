from django.contrib.auth.models import User

from haystack.query import SearchQuerySet

from user_profile.models import Profile

from django.views.decorators.csrf import csrf_exempt

from pin.api6.tools import get_next_url, get_simple_user_object, get_profile_data
from pin.api6.http import return_json_data, return_un_auth, return_not_found,\
    return_bad_request
from pin.views2.dashboard.api.tools import check_admin, cnt_post_deleted_by_user,\
    cnt_post_deleted_by_admin
from pin.models import PhoneData, BannedImei, Log
from pin.tools import get_user_ip


def search_user(request):
    if not check_admin(request):
        return return_un_auth()
    query = request.GET.get('q', '')
    before = int(request.GET.get('before', 0))
    token = request.GET.get('token', '')
    data = {}
    data['meta'] = {'limit': 20, 'next': ""}
    data['objects'] = []

    profiles = SearchQuerySet().models(Profile)\
        .filter(content__contains=query)[before:before + 20]

    for profile in profiles:
        profile = profile.object
        details = {}

        details['user'] = get_simple_user_object(profile.user.id)
        details['profile'] = get_profile_data(profile, profile.user.id)
        details['user']['cnt_deleted'] = cnt_post_deleted_by_user(profile.user.id)
        details['user']['cnt_admin_deleted'] = cnt_post_deleted_by_admin(profile.user.id)
        data['objects'].append(details)

        if data['objects']:
            data['meta']['next'] = get_next_url(url_name='api-6-post-search',
                                                token=token,
                                                before=before + 20)
    return return_json_data(data)


@csrf_exempt
def change_status_user(request):
    if not check_admin(request):
        return return_un_auth()

    user_id = request.POST.get('user_id', False)
    status = request.POST.get('status', 0)
    try:
        user = User.objects.get(pk=user_id)
    except:
        return return_not_found()
    if status == '1':
        user.is_active = True
        message = "User Sttatus Is True."
    else:
        user.is_active = False
        message = "User Sttatus Is False."
    user.save()
    data = {'status': True, 'message': message}
    # TO DO
    # Log
    return return_json_data(data)


@csrf_exempt
def banned_profile(request):
    if not check_admin(request):
        return return_un_auth()

    user_id = request.POST.get('user_id', False)
    description = str(request.POST.get("description", ''))
    status = request.POST.get('status', 0)
    try:
        profile = Profile.objects.get(user_id=user_id)
        user = User.objects.get(pk=user_id)
    except:
        return return_not_found()

    if user_id and description:
        if status == '1':
            profile.banned = True
            profile.save()
        else:
            profile.banned = False
            profile.save()
            Log.ban_by_admin(actor=request.user,
                             user_id=user.id,
                             text="%s || %s" % (user.username, description),
                             ip_address=get_user_ip(request))
        return return_json_data({'status': True,
                                 'message': "Successfully Change Profile banned."})
    else:
        return return_bad_request()


@csrf_exempt
def banned_imei(request):
    if not check_admin(request):
        return return_un_auth()

    imei = str(request.POST.get("imei", ''))
    status = request.POST.get("status", 0)
    user_id = request.POST.get("user_id", '')
    description = str(request.POST.get("description", ''))

    try:
        phone_date = PhoneData.objects.get(imei=imei, user_id=user_id)
    except:
        return return_not_found()
    try:
        user = User.objects.get(id=user_id)
    except:
        return return_not_found()
    if user_id and description and imei:
        if status == '1':
            try:
                banned = BannedImei.objects.get(imei=phone_date.imei)
                banned.delete()
                # TO DO
                # Log Un Banned
            except:
                return return_not_found()
        else:
            BannedImei.objects.create(imei=phone_date.imei, description=description, user=user)
            user.is_active = False
            user.save()
            Log.ban_by_imei(actor=user, text=user.username,
                            ip_address=get_user_ip(request))
