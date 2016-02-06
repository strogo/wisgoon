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
from pin.tools import get_user_ip, AuthCache


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
        user = profile.object.user
        details = {}

        details['user'] = get_simple_user_object(user.id)
        # details['profile'] = get_profile_data(user.profile, user.id)
        # details['user']['cnt_deleted'] = cnt_post_deleted_by_user(user.id)
        # details['user']['cnt_admin_deleted'] = cnt_post_deleted_by_admin(user.id)
        data['objects'].append(details)

        if data['objects']:
            data['meta']['next'] = get_next_url(url_name='api-6-post-search',
                                                token=token,
                                                before=before + 20)
    return return_json_data(data)


def user_details(request, user_id):
    if not check_admin(request):
        return return_un_auth()
    details = {}
    data = {}
    data['meta'] = {'limit': 20, 'next': ""}
    try:
        user = User.objects.get(id=user_id)
    except:
        return return_not_found()
    details['profile'] = get_profile_data(user.profile, user.id)
    details['cnt_deleted'] = cnt_post_deleted_by_user(user.id)
    details['cnt_admin_deleted'] = cnt_post_deleted_by_admin(user.id)
    data['objects'] = details
    return return_json_data(data)


@csrf_exempt
def change_status_user(request):

    if not check_admin(request):
        return return_un_auth()

    try:
        user_id = int(request.POST.get('activeId', False))
        status = str(request.POST.get('activeStatus', False))
        desc = str(request.POST.get('description1', ""))
        user = User.objects.get(pk=user_id)
        # token = request.GET.get('token', False)
        # if token:
        #     current_user = AuthCache.user_from_token(token=token)
        #     if not current_user:
        #         return return_un_auth()
        # else:
        #     return return_bad_request()
    except:
        return return_not_found()

    if user_id:
        if status == '1':
            user.is_active = True
            message = "User Status Is True."
            Log.active_user(user_id=request.user.id,
                            owner=user.id,
                            text=desc + desc,
                            ip_address=get_user_ip(request))
        else:
            user.is_active = False
            message = "User Status Is False."
            Log.ban_by_admin(actor=request.user,
                             user_id=user.id,
                             text="%s || %s" % (user.username, desc),
                             ip_address=get_user_ip(request))

        user.save()
        data = {'status': True, 'message': message}
        data['user'] = get_simple_user_object(user.id)
        data['profile'] = get_profile_data(user.profile, user.id)
        return return_json_data(data)
    else:
        return return_bad_request()


@csrf_exempt
def banned_profile(request):
    if not check_admin(request):
        return return_un_auth()

    try:
        user_id = int(request.POST.get('profileBanId', False))
        status = str(request.POST.get('profileBanstatus', False))
        description = str(request.POST.get('description2', ""))
        profile = Profile.objects.get(user_id=user_id)
        # token = request.GET.get('token', False)
        # if token:
        #     current_user = AuthCache.user_from_token(token=token)
        #     if not current_user:
        #         return return_un_auth()
        # else:
        #     return return_bad_request()
    except:
        return return_not_found()

    if user_id:
        if status == '1':
            profile.banned = True
            profile.save()
            Log.active_user(user_id=request.user.id,
                            owner=profile.user.id,
                            text="%s || %s" % (profile.user.username, description),
                            ip_address=get_user_ip(request))
        else:
            profile.banned = False
            profile.save()
            Log.ban_by_admin(actor=request.user,
                             user_id=profile.user.id,
                             text="%s || %s" % (profile.user.username, description),
                             ip_address=get_user_ip(request))
        data = {'status': True, 'message': "Successfully Change Profile banned."}
        data['user'] = get_simple_user_object(profile.user.id)
        data['profile'] = get_profile_data(profile, profile.user.id)
        data['profile']['description'] = description
        return return_json_data(data)
    else:
        return return_bad_request()


@csrf_exempt
def banned_imei(request):
    if not check_admin(request):
        return return_un_auth()
    try:
        status = str(request.POST.get('status', False))
        description = str(request.POST.get('description3', ""))
        imei = str(request.POST.get('imei', False))
        # token = request.GET.get('token', False)
        # if token:
        #     current_user = AuthCache.user_from_token(token=token)
        #     if not current_user:
        #         return return_un_auth()
        # else:
        #     return return_bad_request()

        phone_date = PhoneData.objects.filter(imei=imei)
    except:
        return return_not_found()
    print description, imei
    if description and imei:
        if status == '1':
            try:
                BannedImei.objects.filter(imei=imei).delete()

                desc = ''
                owner = None

                for data in phone_date:
                    cur_user = data.user
                    owner = cur_user.id
                    desc += cur_user.username + ' || '
                    cur_user.is_active = True
                    cur_user.save()

                Log.active_user(user_id=request.user.id,
                                owner=owner,
                                text=desc + description,
                                ip_address=get_user_ip(request))
                return return_json_data({'status': True,
                                         'message': "Successfully Change Profile banned."})

            except:
                return return_not_found()
        else:
            BannedImei.objects.create(imei=imei,
                                      description=description,
                                      user=request.user)
            desc = ''
            owner = None
            for data in phone_date:
                cur_user = data.user
                owner = cur_user.id
                desc += cur_user.username + ' || '
                cur_user.is_active = False
                cur_user.save()

            Log.ban_by_imei(actor=request.user,
                            text=desc + description,
                            ip_address=get_user_ip(request))
            return return_json_data({'status': True,
                                     'message': "Successfully Change Profile banned."})
    else:
        return return_bad_request()


# @csrf_exempt
# def banned_user_by_imei(request):
#     if not check_admin(request):
#         return return_un_auth()
#     try:
#         json_data = ast.literal_eval(request.body)
#         imei = str(json_data.get('imei'))
#         status = str(json_data.get('status'))
#         description = str(json_data.get('description'))
#         user_id = str(json_data.get('user_id'))

#         phone_date = PhoneData.objects.get(imei=imei, user_id=user_id)
#     except:
#         return return_not_found()

#     try:
#         user = User.objects.get(id=user_id)
#     except:
#         return return_not_found()

#     if user_id and description and imei:
#         if status == 'true':
#             try:
#                 banned = BannedImei.objects.get(imei=phone_date.imei, user=user)
#                 banned.delete()
#                 Log.active_user(user_id=request.user,
#                                 owner=user.id,
#                                 text=description,
#                                 ip_address=get_user_ip(request))
#                 # TO DO
#                 # Log Un Banned
#             except:
#                 return return_not_found()
#         else:
#             BannedImei.objects.create(imei=phone_date.imei,
#                                       description=description,
#                                       user=user)
#             user.is_active = False
#             user.save()
#             Log.ban_by_imei(actor=user, text=user.username,
#                             ip_address=get_user_ip(request))
