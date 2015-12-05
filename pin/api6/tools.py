import ast
from django.core.urlresolvers import reverse
from pin.api_tools import abs_url, media_abs_url
from django.contrib.auth.models import User
from django.conf import settings
from time import time
from pin.forms import PinDirectForm
from io import FileIO, BufferedWriter
from pin.tools import create_filename
from pin.models import Post, Follow
from daddy_avatar.templatetags.daddy_avatar import get_avatar
from pin.cacheLayer import UserDataCache
from pin.models_redis import LikesRedis
from django.utils.translation import ugettext as _


def get_next_url(url_name, offset=None, token=None, url_args={}, **kwargs):
    n_url_p = reverse(url_name, kwargs=url_args) + "?"
    if offset:
        n_url_p = n_url_p + "offset=%s" % (offset)
    if token:
        n_url_p = n_url_p + "&token=%s" % (token)
    for k, v in kwargs.iteritems():
        n_url_p = n_url_p + "&%s=%s" % (k, v)
    return abs_url(n_url_p)


def category_get_json(cat_id):
    from pin.models import Category
    try:
        cat = Category.objects.get(id=cat_id)
    except Category.DoesNotExist:
        raise
    else:
        pass
    finally:
        pass
    cat_json = {
        'id': cat.id,
        'image': media_abs_url(cat.image.url),
        'title': cat.title,
    }
    return cat_json


def get_int(number):
    try:
        post_id = int(number)
    except ValueError:
        post_id = 0
    return post_id


def get_json(data):
    try:
        to_json = ast.literal_eval(data)
    except ValueError:
        to_json = False
    return to_json


# def get_user_data(user_id):
#     user_data = {}
#     avatar = ''
#     try:
#         user = User.objects.get(id=user_id)
#         user_data['id'] = user.id
#         user_data['username'] = user.username
#         if user.profile.avatar:
#             avatar = media_abs_url(str(user.profile.avatar))
#         user_data['avatar'] = avatar
#     except Exception as e:
#         print e
#     return user_data


def get_category(cat_id):
    from pin.models import Category
    try:
        cat = Category.objects.get(id=get_int(cat_id))
    except Category.DoesNotExist:
        cat = False
    return cat


def save_post(request, user):

    media_url = settings.MEDIA_ROOT

    model = None
    form = PinDirectForm(request.POST, request.FILES)
    if form.is_valid():
        upload = request.FILES.values()[0]
        filename = create_filename(upload.name)
        try:
            u = "%s/pin/%s/images/o/%s" % (media_url, settings.INSTANCE_NAME, filename)
            with BufferedWriter(FileIO(u, "wb")) as dest:
                for c in upload.chunks():
                    dest.write(c)

            model = Post()
            model.image = "pin/%s/images/o/%s" % (settings.INSTANCE_NAME, filename)
            model.user = user
            model.timestamp = time()
            model.text = form.cleaned_data['description']
            model.category_id = form.cleaned_data['category']
            model.device = 2
            model.save()
            status = True
            msg = _("Successfully Send Post")
        except IOError, e:
            status = False
            msg = str(e)
    else:
        msg = form.errors
        status = False
    return status, model, msg


def get_list_post(pl, from_model='latest'):
    arp = []

    for pll in pl:
        try:
            arp.append(Post.objects.only(*Post.NEED_KEYS2).get(id=pll))
        except Exception:
            pass

    posts = arp
    return posts


def get_simple_user_object(current_user, user_id_from_token=None):
    user_info = {}
    user_info['id'] = current_user
    user_info['avatar'] = media_abs_url(get_avatar(current_user, size=64))
    user_info['username'] = UserDataCache.get_user_name(current_user)
    user_info['related'] = {}

    user_info['related']['posts'] = abs_url(reverse('api-6-post-user', kwargs={'user_id': current_user}))
    if user_id_from_token:
        user_info['follow_by_user'] = Follow.objects\
            .filter(follower_id=current_user, following_id=user_id_from_token)\
            .exists()
    else:
        user_info['follow_by_user'] = False

    return user_info


def get_last_likers(post_id, limit=3):
    from pin.models_redis import LikesRedis
    l = LikesRedis(post_id=post_id)\
        .get_likes(offset=0, limit=limit, as_user_object=False)

    likers_list = []
    for ll in l:
        ll = int(ll)
        u = {
            'user': get_simple_user_object(ll)
        }
        likers_list.append(u)

    return likers_list


def get_objects_list(posts, cur_user_id=None, r=None):

    objects_list = []
    for p in posts:
        if not p:
            continue

        try:
            if p.is_pending():
                continue
        except Post.DoesNotExist:
            continue

        o = {}

        o['id'] = p.id
        o['text'] = p.text
        o['cnt_comment'] = 0 if p.cnt_comment == -1 else p.cnt_comment
        o['timestamp'] = p.timestamp

        o['user'] = get_simple_user_object(p.user_id)

        o['last_likers'] = get_last_likers(post_id=p.id)

        try:
            o['url'] = p.url
        except Exception, e:
            print str(e)
            if r:
                print r.get_full_path()
            o['url'] = None
        o['cnt_like'] = p.cnt_like
        o['like_with_user'] = False
        o['status'] = p.status

        try:
            o['is_ad'] = False  # p.is_ad
        except Exception, e:
            # print str(e)
            o['is_ad'] = False

        o['permalink'] = {}

        o['permalink']['api'] = abs_url(reverse("api-6-post-item",
                                                kwargs={"item_id": p.id}))

        o['permalink']['web'] = abs_url(reverse("pin-item",
                                                kwargs={"item_id": p.id}),
                                        api=False)

        if cur_user_id:
            o['like_with_user'] = LikesRedis(post_id=p.id)\
                .user_liked(user_id=cur_user_id)

        o['images'] = {}
        try:
            p_500 = p.get_image_500(api=True)

            p_500['url'] = media_abs_url(p_500['url'])
            p_500['height'] = int(p_500['hw'].split("x")[0])
            p_500['width'] = int(p_500['hw'].split("x")[1])

            del(p_500['hw'])
            del(p_500['h'])

            o['images']['low_resolution'] = p_500
            # o['images']['low_resolution']['url'] = media_abs_url(p_500['url'])
            # o['images']['low_resolution']['height'] = int(p_500['hw'].split("x")[0])
            # o['images']['low_resolution']['width'] = int(p_500['hw'].split("x")[1])
            # del(o['images']['low_resolution']['hw'])
            # del(o['images']['low_resolution']['h'])

            p_236 = p.get_image_236(api=True)

            p_236['url'] = media_abs_url(p_236['url'])
            p_236['height'] = int(p_236['hw'].split("x")[0])
            p_236['width'] = int(p_236['hw'].split("x")[1])
            del(p_236['hw'])
            del(p_236['h'])

            o['images']['thumbnail'] = p_236

            p_original = p.get_image_sizes()
            o['images']['original'] = p_original
            o['images']['original']['url'] = media_abs_url(p.image)
        except Exception, e:
            continue

        o['category'] = category_get_json(cat_id=p.category_id)
        objects_list.append(o)

    return objects_list


def get_profile_data(profile, user_id):
    update_follower_following(profile, user_id)
    data = {}
    data['name'] = profile.name
    data['score'] = profile.score
    data['cnt_post'] = profile.cnt_post
    data['cnt_like'] = profile.cnt_like
    data['is_active'] = profile.user.is_active
    data['credit'] = profile.credit
    data['cnt_follower'] = profile.cnt_follower
    data['cnt_following'] = profile.cnt_following
    return data


def update_follower_following(profile, user_id):
    from pin.api6.http import return_bad_request
    try:
        profile.cnt_follower = Follow.objects.filter(following_id=user_id).count()
        profile.cnt_following = Follow.objects.filter(follower_id=user_id).count()
    except:
        return return_bad_request()
