import ast
import urllib
from io import FileIO, BufferedWriter
from time import time

from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.utils.timezone import localtime

from daddy_avatar.templatetags.daddy_avatar import get_avatar

from pin.api_tools import abs_url, media_abs_url
from pin.api6.http import return_bad_request
from pin.cacheLayer import UserDataCache
from pin.forms import PinDirectForm
from pin.models import Post, Follow, Comments, Block, Category
from pin.models_redis import LikesRedis, PostView
from pin.tools import create_filename

from cache_layer import PostCacheLayer

import khayyam

VERB = {5: "Create post", 6: "Comment", 7: "Like",
        8: "Follow", 9: "request follow", 10: "accept follow"}


def get_next_url(url_name, offset=None, token=None, url_args={}, **kwargs):
    n_url_p = reverse(url_name, kwargs=url_args) + "?"
    d = {}
    if offset:
        d['offset'] = offset
    if token:
        d['token'] = token
    for k, v in kwargs.iteritems():
        d[k] = v
    n_url_p += urllib.urlencode(d)
    return abs_url(n_url_p)


def category_get_json(cat_id):
    try:
        cat = Category.objects.get(id=cat_id)
    except Category.DoesNotExist:
        raise

    cat_json = {
        'id': cat.id,
        'image': media_abs_url(cat.image.url, static=True),
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


def get_category(cat_id):
    try:
        cat = Category.objects.get(id=get_int(cat_id))
    except Category.DoesNotExist:
        cat = False
    return cat


def save_post(request, user):
    media_url = settings.MEDIA_ROOT
    model = None

    try:
        form = PinDirectForm(request.POST, request.FILES)
    except Exception, e:
        msg = "error in data"
        status = False
        return status, model, msg

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
            model.device = Post.DEVICE_MOBILE_6
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
        arp.append(int(pll))

    posts = arp
    return posts


def get_simple_user_object(current_user, user_id_from_token=None, avatar=64):
    user_info = {}
    user_info['id'] = current_user
    if avatar == 64:
        user_info['avatar'] = media_abs_url(get_avatar(current_user, size=64), check_photos=True)
    else:
        user_info['avatar'] = media_abs_url(get_avatar(current_user), check_photos=True)
    user_info['username'] = UserDataCache.get_user_name(current_user)
    user_info['related'] = {}
    user_info['follow_by_user'] = False
    user_info['block_by_user'] = False

    user_info['related']['posts'] = abs_url(reverse('api-6-post-user',
                                                    kwargs={
                                                        'user_id': current_user
                                                    }))
    user_info['permalink'] = abs_url(reverse("pin-absuser",
                                             kwargs={"user_name": user_info['username']}))
    if user_id_from_token:
        user_info['follow_by_user'] = Follow.objects\
            .filter(follower_id=user_id_from_token, following_id=current_user)\
            .exists()

        user_info['block_by_user'] = Block.objects\
            .filter(user_id=user_id_from_token, blocked_id=current_user)\
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


def get_last_comments(post_id, limit=3):
    comments = get_comments(post_id, limit, 0)
    return comment_objects_list(comments)


def get_post_tags(post):
    tags = []
    for tag in post.get_tags():
        tag_url = abs_url(reverse("api-6-post-hashtag",
                                  kwargs={"tag_name": tag}),
                          api=False)
        web_tag_url = abs_url(reverse("hashtags",
                                      kwargs={"tag_name": tag}),
                              api=False)
        tags.append({
            'title': tag,
            'permalink': {
                'web': web_tag_url,
                'api': tag_url
            }
        })

    return tags


def post_item_json(post_id, cur_user_id=None, r=None, fields=None, exclude=None):

    if not post_id:
        return {}

    post_id = int(post_id)

    def need_fields(post_object):

        final_o = {}
        if fields:
            final_o = {f: post_object[f] for f in fields}
        else:
            final_o = post_object

        if exclude:
            if not fields:
                final_o = post_object

            for f in exclude:
                try:
                    final_o.pop(f)
                except:
                    pass

        return final_o

    pi = {}  # post item

    if post_id:
        cp = PostCacheLayer(post_id=post_id)

        cache_post = cp.get()
        pi['cnt_view'] = PostView(post_id=post_id).get_cnt_view()
        PostView(post_id=post_id).inc_view()
        if cache_post:
            if cur_user_id:
                cache_post['like_with_user'] = LikesRedis(post_id=post_id)\
                    .user_liked(user_id=cur_user_id)
            cache_post['cnt_view'] = pi['cnt_view']
            cache_post['cache'] = "Hit"
            cache_post = need_fields(cache_post)
            return cache_post

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            return None
        pi['cache'] = "Miss"
        pi['id'] = post.id
        pi['text'] = post.text
        pi['cnt_comment'] = 0 if post.cnt_comment == -1 else post.cnt_comment
        pi['timestamp'] = post.timestamp
        pi['show_in_default'] = post.show_in_default

        pi['user'] = get_simple_user_object(post.user_id)

        pi['last_likers'] = get_last_likers(post_id=post.id)
        pi['last_comments'] = get_last_comments(post_id=post.id)

        pi['url'] = post.url

        pi['cnt_like'] = post.cnt_like
        pi['like_with_user'] = False
        pi['status'] = post.status

        pi['tags'] = get_post_tags(post)

        pi['is_ad'] = False

        pi['permalink'] = {}

        pi['permalink']['api'] = abs_url(reverse("api-6-post-item",
                                         kwargs={"item_id": post.id}))

        pi['permalink']['web'] = abs_url(reverse("pin-item",
                                         kwargs={"item_id": post.id}),
                                         api=False)

        if cur_user_id:
            pi['like_with_user'] = LikesRedis(post_id=post.id)\
                .user_liked(user_id=cur_user_id)

        pi['images'] = {
            'thumbnail': {},
            'original': {},
            'low_resolution': {}
        }
        try:
            p_500 = post.get_image_500(api=True)

            p_500['url'] = media_abs_url(p_500['url'], check_photos=True)
            p_500['height'] = int(p_500['hw'].split("x")[0])
            p_500['width'] = int(p_500['hw'].split("x")[1])

            del(p_500['hw'])
            del(p_500['h'])

            pi['images']['low_resolution'] = p_500
        except Exception:
            pass

        try:
            p_236 = post.get_image_236(api=True)

            p_236['url'] = media_abs_url(p_236['url'], check_photos=True)
            p_236['height'] = int(p_236['hw'].split("x")[0])
            p_236['width'] = int(p_236['hw'].split("x")[1])
            del(p_236['hw'])
            del(p_236['h'])

            pi['images']['thumbnail'] = p_236

        except Exception:
            pass

        try:
            p_original = post.get_image_sizes()
            pi['images']['original'] = p_original
            pi['images']['original']['url'] = media_abs_url(post.image,
                                                            check_photos=True)
        except Exception:
            pass

        pi['category'] = category_get_json(cat_id=post.category_id)

        cp.set(pi)
        pi = need_fields(pi)
    return pi


def get_objects_list(posts, cur_user_id=None, r=None):
    objects_list = []
    for post in posts:
        if not post:
            continue

        post_item = post_item_json(post, cur_user_id, r)
        if post_item:
            objects_list.append(post_item)

    return objects_list


def get_profile_data(profile, user_id):
    update_follower_following(profile, user_id)
    data = {}
    data['name'] = profile.name
    data['score'] = profile.score
    data['cnt_post'] = profile.cnt_post
    data['cnt_like'] = profile.cnt_like
    data['is_active'] = str(profile.user.is_active)
    data['credit'] = profile.credit
    data['cnt_follower'] = profile.cnt_follower
    data['cnt_following'] = profile.cnt_following
    data['banned'] = profile.banned
    if profile.cover:
        data['cover'] = media_abs_url(profile.cover.url, check_photos=True)
    else:
        data['cover'] = ""
    data['score'] = profile.score
    data['jens'] = profile.jens if profile.jens else '0'
    data['bio'] = profile.bio
    data['date_joined'] = khayyam.JalaliDate(profile.user.date_joined)\
        .strftime("%Y/%m/%d")

    return data


def update_follower_following(profile, user_id):
    try:
        profile.cnt_follower = Follow.objects.filter(following_id=user_id)\
            .count()
        profile.cnt_following = Follow.objects.filter(follower_id=user_id)\
            .count()
    except:
        return return_bad_request()


def get_comments(post_id, limit, before):
    try:
        comments = Comments.objects\
            .filter(object_pk_id=post_id)\
            .order_by('-id')[before: before + limit]
    except:
        comments = []
    return comments


def comment_item_json(comment):
    comment_dict = {}
    comment_dict['id'] = comment.id
    comment_dict['comment'] = comment.comment
    comment_dict['user'] = get_simple_user_object(comment.user.id)
    d = localtime(comment.submit_date)
    comment_dict['date'] = int(d.strftime("%s"))
    return comment_dict


def comment_objects_list(comments):
    comments_list = []
    for comment in comments:
        comment_dict = comment_item_json(comment)
        comments_list.append(comment_dict)
    return comments_list


def ad_item_json(ad):
    ad_dict = {}
    ad_dict['post'] = post_item_json(ad.post.id)
    ad_dict['cnt_view'] = ad.get_cnt_view()
    ad_dict['user'] = get_simple_user_object(ad.user.id)
    ad_dict['ended'] = ad.ended
    ad_dict['ads_type'] = ad.ads_type
    ad_dict['start'] = str(ad.start)
    ad_dict['end'] = str(ad.end)
    ad_dict['id'] = ad.id
    return ad_dict


def new_reported(post):
    new_report = {}
    new_report['reported_post'] = post_item_json(post.post.id)
    return new_report


def notif_simple_json(notification, user=True, post=True,
                      text=False):
    notif_dict = {}
    notif_dict['verb'] = VERB[notification.verb.id]
    notif_dict['other_actor_count'] = notification.other_actor_count
    notif_dict['user'] = {}
    notif_dict['post'] = {}
    notif_dict['text'] = ''
    notif_dict['activity_ids'] = notification.activity_ids
    notif_dict['is_seen'] = notification.is_seen

    if user:
        notif_dict['user'] = get_simple_user_object(current_user=notification.actor_ids[-1])

    if post:
        notif_dict['post'] = post_item_json(post_id=notification.object_ids[0])

    if text:
        notif_dict['text'] = notification.activities[-1].extra_context['text']

    return notif_dict
