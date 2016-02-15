from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt

from haystack.query import SearchQuerySet
from haystack.query import SQ
from haystack.query import Raw

from pin.tools import get_user_ip
from pin.api_tools import media_abs_url
from pin.models import PhoneData, BannedImei, Log
from pin.views2.dashboard.api.tools import get_profile_data
from pin.api6.tools import get_next_url, get_simple_user_object
from pin.api6.http import return_json_data, return_un_auth, return_not_found,\
    return_bad_request
from pin.views2.dashboard.api.tools import check_admin,\
    cnt_post_deleted_by_user, cnt_post_deleted_by_admin

from user_profile.models import Profile

from daddy_avatar.templatetags.daddy_avatar import get_avatar

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

    words = query.split()
    sq = SQ()
    for w in words:
        sq.add(SQ(text__contains=Raw("%s*" % w)), SQ.OR)
        sq.add(SQ(text__contains=Raw(w)), SQ.OR)

    results = SearchQuerySet().models(Profile).filter(sq)[before:before + 20]

    for result in results:
        user = result.object.user
        details = {}

        details['username'] = user.username
        details['avatar'] = media_abs_url(get_avatar(user.id, size=64))
        details['id'] = user.id
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

    details['profile'] = get_profile_data(user.profile, enable_imei=True)
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
    except:
        return return_not_found()

    if user_id:
        if status == '1':
            user.is_active = True
            message = "User Status Is True."
            # Log.active_user(user_id=request.user.id,
            #                 owner=user.id,
            #                 text=desc + desc,
            #                 ip_address=get_user_ip(request))
        else:
            user.is_active = False
            message = "User Status Is False."
            # Log.ban_by_admin(actor=request.user,
            #                  user_id=user.id,
            #                  text="%s || %s" % (user.username, desc),
            #                  ip_address=get_user_ip(request))

        user.save()
        data = {'status': True, 'message': message}
        data['user'] = get_simple_user_object(user.id)
        data['profile'] = get_profile_data(user.profile)
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
    except:
        return return_not_found()

    if user_id:
        if status == '1':
            profile.banned = True
            profile.save()
            # Log.active_user(user_id=request.user.id,
            #                 owner=profile.user.id,
            #                 text="%s || %s" % (profile.user.username, description),
            #                 ip_address=get_user_ip(request))
        else:
            profile.banned = False
            profile.save()
            # Log.ban_by_admin(actor=request.user,
            #                  user_id=profile.user.id,
            #                  text="%s || %s" % (profile.user.username, description),
            #                  ip_address=get_user_ip(request))
        data = {'status': True, 'message': "Successfully Change Profile banned."}
        data['user'] = get_simple_user_object(profile.user.id)
        data['profile'] = get_profile_data(profile)
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
        phone_date = PhoneData.objects.filter(imei=imei)
    except:
        return return_not_found()

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
                                         'message': "Successfully banned Imei."})

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
                                     'message': "Successfully banned Imei."})
    else:
        return return_bad_request()


def get_user_with_imei(request, imei):
    if not check_admin(request):
        return return_un_auth()

    users = []
    data = {}
    data['meta'] = {'limit': '',
                    'next': '',
                    'total_count': ''}

    phone_data = PhoneData.objects.filter(imei=imei)

    for data in phone_data:
        users.append(get_simple_user_object(data.user.id))

    data['objects'] = users
    return users
