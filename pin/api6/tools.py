import ast
from io import FileIO, BufferedWriter
from time import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from daddy_avatar.templatetags.daddy_avatar import get_avatar

from pin.api_tools import abs_url, media_abs_url
from pin.cacheLayer import UserDataCache
from pin.forms import PinDirectForm
from pin.models import Post, Follow
from pin.models_redis import LikesRedis
from pin.tools import create_filename
from cache_layer import PostCacheLayer


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
            u = "{}/pin/{}/images/o/{}".\
                format(media_url, settings.INSTANCE_NAME, filename)
            with BufferedWriter(FileIO(u, "wb")) as dest:
                for c in upload.chunks():
                    dest.write(c)

            model = Post()
            model.image = "pin/{}/images/o/{}".\
                format(settings.INSTANCE_NAME, filename)
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
    user_info['follow_by_user'] = False

    user_info['related']['posts'] = abs_url(reverse('api-6-post-user',
                                                    kwargs={
                                                        'user_id': current_user
                                                    }))
    if user_id_from_token:
        user_info['follow_by_user'] = Follow.objects\
            .filter(follower_id=user_id_from_token, following_id=current_user)\
            .exists()

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


def post_item_json(post, cur_user_id=None, r=None):
    cp = PostCacheLayer(post_id=post.id)
    cache_post = cp.get()

    if cache_post:
        print "get post data item json from cache"
        return cache_post

    post_item = {}

    post_item['id'] = post.id
    post_item['text'] = post.text
    post_item['cnt_comment'] = 0 if post.cnt_comment == -1 else post.cnt_comment
    post_item['timestamp'] = post.timestamp

    post_item['user'] = get_simple_user_object(post.user_id)

    post_item['last_likers'] = get_last_likers(post_id=post.id)

    try:
        post_item['url'] = post.url
    except Exception, e:
        print str(e)
        if r:
            print r.get_full_path()
        post_item['url'] = None
    post_item['cnt_like'] = post.cnt_like
    post_item['like_with_user'] = False
    post_item['status'] = post.status

    try:
        post_item['is_ad'] = False  # post.is_ad
    except Exception, e:
        # print str(e)
        post_item['is_ad'] = False

    post_item['permalink'] = {}

    post_item['permalink']['api'] = abs_url(reverse("api-6-post-item",
                                            kwargs={"item_id": post.id}))

    post_item['permalink']['web'] = abs_url(reverse("pin-item",
                                            kwargs={"item_id": post.id}),
                                            api=False)

    if cur_user_id:
        post_item['like_with_user'] = LikesRedis(post_id=post.id)\
            .user_liked(user_id=cur_user_id)

    post_item['images'] = {}
    try:
        p_500 = post.get_image_500(api=True)

        p_500['url'] = media_abs_url(p_500['url'])
        p_500['height'] = int(p_500['hw'].split("x")[0])
        p_500['width'] = int(p_500['hw'].split("x")[1])

        del(p_500['hw'])
        del(p_500['h'])

        post_item['images']['low_resolution'] = p_500

        p_236 = post.get_image_236(api=True)

        p_236['url'] = media_abs_url(p_236['url'])
        p_236['height'] = int(p_236['hw'].split("x")[0])
        p_236['width'] = int(p_236['hw'].split("x")[1])
        del(p_236['hw'])
        del(p_236['h'])

        post_item['images']['thumbnail'] = p_236

        p_original = post.get_image_sizes()
        post_item['images']['original'] = p_original
        post_item['images']['original']['url'] = media_abs_url(post.image)
    except Exception as e:
        print str(e)

    post_item['category'] = category_get_json(cat_id=post.category_id)

    cp.set(post_item)
    return post_item


def get_objects_list(posts, cur_user_id=None, r=None):

    objects_list = []
    for post in posts:
        if not post:
            continue

        try:
            if post.is_pending():
                continue
        except Post.DoesNotExist:
            continue

        post_item = post_item_json(post, cur_user_id, r)
        objects_list.append(post_item)

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
        profile.cnt_follower = Follow.objects.filter(following_id=user_id)\
            .count()
        profile.cnt_following = Follow.objects.filter(follower_id=user_id)\
            .count()
    except:
        return return_bad_request()
