from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _
from django.views.decorators.csrf import csrf_exempt

from haystack.query import Raw
from haystack.query import SearchQuerySet
from haystack.query import SQ

from pin.api6.tools import get_next_url, get_simple_user_object
from pin.api6.http import return_json_data, return_un_auth, return_not_found,\
    return_bad_request
from pin.api_tools import media_abs_url
from pin.models import PhoneData, BannedImei, Log
from pin.tools import get_user_ip
from pin.views2.dashboard.api.tools import get_profile_data, check_admin,\
    cnt_post_deleted_by_admin

from user_profile.models import Profile

from daddy_avatar.templatetags.daddy_avatar import get_avatar


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
    user_profile, created = Profile.objects.get_or_create(user_id=user_id)

    details['profile'] = get_profile_data(user.profile, enable_imei=True)

    ban_profile_log = Log.objects\
        .filter(object_id=user.id, content_type=Log.USER,
                action=Log.BAN_ADMIN).order_by('-id')[:1]

    ban_imei_log = BannedImei.objects\
        .filter(owner=user.id).order_by('-id')[:1]

    active_log = Log.objects\
        .filter(owner=user.id, content_type=Log.USER,
                action=Log.ACTIVE_USER).order_by('-id')[:1]

    inactive_log = Log.objects\
        .filter(owner=user.id, content_type=Log.USER,
                action=Log.BAN_ADMIN).order_by('-id')[:1]

    details['profile']['ban_profile_desc'] = str(ban_profile_log[0].text) if ban_profile_log else ''
    details['profile']['ban_imei_desc'] = str(ban_imei_log[0].description) if ban_imei_log else ''
    details['profile']['active_desc'] = str(active_log[0].text) if active_log else ''
    details['profile']['inactive_desc'] = str(inactive_log[0].text) if inactive_log else ''
    details['user_id'] = int(user_id)
    details['cnt_post'] = user_profile.cnt_post
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

    if settings.DEBUG:
        from pin.tools import AuthCache
        token = request.GET.get('token', '')
        if token:
            current_user = AuthCache.user_from_token(token=token)
        else:
            current_user = request.user
    else:
        current_user = request.user

    if user_id:
        if status == 'true':
            user.is_active = True
            message = _("User Status Is True.")
            Log.active_user(user_id=current_user.id,
                            owner=user.id,
                            text=desc + desc,
                            ip_address=get_user_ip(request))
        else:
            user.is_active = False
            message = _("User Status Is False.")
            Log.deactive_user(user_id=current_user.id,
                              owner=user.id,
                              text=desc + desc,
                              ip_address=get_user_ip(request))

        user.save()
        data = {'status': True, 'message': message}
        data['user'] = get_simple_user_object(user.id)
        data['profile'] = get_profile_data(user.profile)
        data['profile']['description1'] = desc
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

    if settings.DEBUG:
        from pin.tools import AuthCache
        token = request.GET.get('token', '')
        if token:
            current_user = AuthCache.user_from_token(token=token)
        else:
            current_user = request.user
    else:
        current_user = request.user

    if user_id:
        if status == 'true':
            profile.banned = True
            profile.save()
            Log.active_user(user_id=current_user.id,
                            owner=profile.user.id,
                            text="%s || %s" % (profile.user.username, description),
                            ip_address=get_user_ip(request))
        else:
            profile.banned = False
            profile.save()
            Log.ban_by_admin(actor=current_user,
                             user_id=profile.user.id,
                             text="%s || %s" % (profile.user.username, description),
                             ip_address=get_user_ip(request))
        data = {
            'status': True,
            'message': _("Successfully Change Profile banned.")
        }
        data['user'] = get_simple_user_object(profile.user.id)
        data['profile'] = get_profile_data(profile)
        data['profile']['description2'] = description
        return return_json_data(data)
    else:
        return return_bad_request()


@csrf_exempt
def banned_imei(request):
    if not check_admin(request):
        return return_un_auth()

    phone_data = None
    try:
        status = str(request.POST.get('status', 0))
        description = str(request.POST.get('description3', ""))
        imei = request.POST.get('imei', None)
        phone_data = PhoneData.objects.filter(imei=imei)
    except:
        return return_not_found()

    if settings.DEBUG:
        from pin.tools import AuthCache
        token = request.GET.get('token', '')
        if token:
            current_user = AuthCache.user_from_token(token=token)
        else:
            current_user = request.user
    else:
        current_user = request.user

    if description and imei:

        if status == 'true':
            try:
                BannedImei.objects.filter(imei=imei).delete()

                desc = ''
                owner = None

                for data in phone_data:
                    cur_user = data.user
                    owner = cur_user.id
                    desc += cur_user.username + ' || '
                    cur_user.is_active = True
                    cur_user.save()

                Log.active_user(user_id=current_user.id,
                                owner=owner,
                                text=desc + description,
                                ip_address=get_user_ip(request))
                return return_json_data({'status': True,
                                         'message': _("Successfully Unbanned Imei."),
                                         'imei_status': True})

            except:
                return return_not_found()

        elif status == 'false':
            BannedImei.objects.create(imei=imei,
                                      description=description,
                                      user=current_user)

            desc = ''
            owner = None
            for data in phone_data:
                cur_user = data.user
                owner = cur_user.id
                desc += cur_user.username + ' || '
                cur_user.is_active = False
                cur_user.save()
            Log.ban_by_imei(actor=current_user,
                            text=desc + description,
                            ip_address=get_user_ip(request))

            return return_json_data({'status': True,
                                     'message': _("Successfully banned Imei."),
                                     'imei_status': False})
        else:
            return return_bad_request(message=_('Status Not Valid'))
    else:

        return return_bad_request()


def get_user_with_imei(request, imei):
    if not check_admin(request):
        return return_un_auth()

    users = []
    result = {}
    result['meta'] = {'limit': '',
                      'next': '',
                      'total_count': ''}

    phone_data = PhoneData.objects.filter(imei=imei)
    for data in phone_data:
        users.append(get_simple_user_object(data.user.id))
        print users

    result['objects'] = users
    return return_json_data(result)


def delete_user_avatar(request, user_id):
    if not check_admin(request):
        return return_un_auth()
    try:
        profile = Profile.objects.get(user_id=user_id)
    except Exception, e:
        print str(e), "func :dashboard/api/ delete user profile"
        return return_not_found()

    profile.avatar = None
    profile.delete_avatar_cache()
    profile.save()
    data = {'status': True, 'message': _('Successfully removed.')}
    return return_json_data(data)
