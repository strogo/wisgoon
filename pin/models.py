# -*- coding: utf-8 -*-
import emoji
import hashlib
import os
import re
import time
import PIL
from datetime import datetime, timedelta
from time import mktime

from PIL import Image

from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.db import models
from django.db.models import F, Q
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

import redis

from preprocessing import normalize_tags

from model_mongo import MonthlyStats
from sorl.thumbnail import get_thumbnail
from textblob.classifiers import NaiveBayesClassifier


from pin.tasks import delete_image
from pin.classification_tools import normalize
from pin.api6.cache_layer import PostCacheLayer
from pin.models_graph import FollowUser
from pin.models_stream import RedisUserStream
from models_casper import CatStreams
from pin.models_es import ESPosts

# from pin.analytics import comment_act, post_act


LIKE_TO_DEFAULT_PAGE = 10
# r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)
r_server = redis.Redis(settings.REDIS_DB_2, db=settings.REDIS_DB_NUMBER)
r_server4 = redis.Redis(settings.REDIS_DB_2, db=4)


class Storages(models.Model):
    name = models.CharField(max_length=100)
    used = models.BigIntegerField(default=0)
    num_files = models.IntegerField(default=0)
    path = models.CharField(max_length=250)
    host = models.CharField(max_length=100)
    user = models.CharField(max_length=30)


class CommentClassificationTags(models.Model):
    name = models.CharField(max_length=50)

    def __unicode__(self):
        return self.name


class CommentClassification(models.Model):
    CACHE_NAME = 'com:cl'
    CACHE_TTL = 86400

    text = models.TextField()
    tag = models.ForeignKey(CommentClassificationTags)

    def __unicode__(self):
        return self.text

    def get_text(self):
        return normalize(self.text)

    def save(self, *args, **kwargs):
        super(CommentClassification, self).save(*args, **kwargs)
        train = []
        for cc in CommentClassification.objects.all():
            txt = u"%s" % cc.get_text()
            train.append((txt, cc.tag_id))

        cl = NaiveBayesClassifier(train)
        cache.set(self.CACHE_NAME, cl, self.CACHE_TTL)


class SubCategory(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(default='', upload_to='pin/scategory/')
    image_device = models.ImageField(default='', upload_to='pin/scategory/')
    cnt_post = models.IntegerField(default=0)

    def __unicode__(self):
        return self.title

    def admin_image(self):
        return '<img src="/media/{}" />'.format(self.image)

    def admin_image_device(self):
        return '<img src="/media/{}" />'.format(self.image_device)

    admin_image.allow_tags = True
    admin_image_device.allow_tags = True


class Ad(models.Model):
    TYPE_1000_USER = 1
    TYPE_3000_USER = 2
    TYPE_6000_USER = 3
    TYPE_15000_USER = 4

    MAX_TYPES = {
        TYPE_1000_USER: 1000,
        TYPE_3000_USER: 3000,
        TYPE_6000_USER: 6000,
        TYPE_15000_USER: 15000,
    }

    TYPE_PRICES = {
        TYPE_1000_USER: 500,
        TYPE_3000_USER: 1000,
        TYPE_6000_USER: 2000,
        TYPE_15000_USER: 5000,
    }

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='owner',
                              blank=True, null=True)
    ended = models.BooleanField(default=False, db_index=True)
    cnt_view = models.IntegerField(default=0)
    post = models.ForeignKey("Post")
    ads_type = models.IntegerField(default=TYPE_1000_USER)
    start = models.DateTimeField(auto_now=True)
    end = models.DateTimeField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(default="127.0.0.1")

    def get_cnt_view(self):
        cache_key = "ad_%d" % self.id
        v = cache.get(cache_key)
        if v:
            return v
        else:
            return self.cnt_view

    @classmethod
    def get_ad(cls, user_id, high_level=False):
        if cache.get("no_ad"):
            return None

        if not Ad.objects.filter(ended=False).exists():
            cache.set("no_ad", True, 86400)
            return None

        if high_level:
            query_set = Ad.objects.filter(ended=False,
                                          ads_type=cls.TYPE_15000_USER)
        else:
            query_set = Ad.objects.filter(ended=False)

        for ad in query_set:
            cache_key = "ad_%d" % ad.id
            redis_ad_key = "ad_%d" % ad.id

            if not cache.get(cache_key):
                cache.set(cache_key, 0, 86400 * 30)

            if r_server.sismember(redis_ad_key, user_id):
                continue
            else:
                r_server.sadd(redis_ad_key, user_id)

            if ad.get_cnt_view() >= cls.MAX_TYPES[ad.ads_type]:
                Ad.objects.filter(id=ad.id)\
                    .update(cnt_view=ad.get_cnt_view(),
                            end=datetime.now(),
                            ended=True)
                r_server.delete(redis_ad_key)
            else:
                try:
                    cache.incr(cache_key)
                except:
                    pass

            return ad

        return None

    def save(self, *args, **kwargs):
        cache.delete("no_ad")
        self.owner = self.post.user
        MonthlyStats.log_hit(MonthlyStats.ADS)
        super(Ad, self).save(*args, **kwargs)


class Category(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(default='', upload_to='pin/category/')
    parent = models.ForeignKey(SubCategory, related_name='sub_category',
                               blank=True, null=True)
    cnt_post = models.IntegerField(default=0)
    native_hashcode = models.CharField(max_length=255, blank=True, null=True)

    def __unicode__(self):
        return self.title

    def admin_image(self):
        return '<img src="/media/{}" />'.format(self.image)

    admin_image.allow_tags = True

    @classmethod
    def get_json(cls, cat_id):
        jccs = "json_cat_%s" % cat_id
        jcc = cache.get(jccs)
        if jcc:
            return jcc

        cat = Category.objects.get(id=cat_id)
        cat_json = {
            'id': cat.id,
            'image': cat.image.url,
            'resource_uri': "/pin/apic/category/" + str(cat.id) + "/",
            'title': cat.title,
        }
        cache.set(jccs, cat_json, 86400)
        return cat_json


class Sim(models.Model):
    post = models.OneToOneField('Post')
    features = models.TextField()


class Packages(models.Model):
    title = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    wis = models.IntegerField(default=0)
    price = models.IntegerField(default=0)
    icon = models.ImageField(upload_to="packages/")


class Post(models.Model):

    GLOBAL_LIMIT = 10
    MLT_CACHE_STR = "mlt:2{}{}"
    MLT_CACHE_TTL = 43200  # 12 hours

    HOME_QUEUE_NAME = "home_queue"

    PENDING = 0
    APPROVED = 1
    FAULT = 2

    META_DATA = None

    NEED_KEYS = ['id', 'text', 'cnt_comment', 'timestamp',
                 'image', 'user_id', 'cnt_like', 'category_id',
                 'status', 'url', 'report']

    NEED_KEYS2 = ['id', 'text', 'cnt_comment', 'timestamp',
                  'image', 'user', 'cnt_like', 'category',
                  'status', 'url', 'report']

    NEED_KEYS_WEB = ['id', 'text', 'cnt_comment', 'cnt_like', 'user',
                     'show_in_default', 'timestamp', 'report']

    STATUS_CHOICES = (
        (PENDING, _('Pending')),
        (APPROVED, _('Accepted')),
        (FAULT, _('Violation')),
    )

    DEVICE_WEB = 1
    DEVICE_MOBILE_2 = 2
    DEVICE_MOBILE_6 = 3

    DEVICE_CHOICES = (
        (DEVICE_WEB, "web"),
        (DEVICE_MOBILE_2, "mobile version 2"),
        (DEVICE_MOBILE_6, "mobile version 6"),
    )

    text = models.TextField(blank=True, verbose_name=_('Text'))
    image = models.CharField(max_length=500, verbose_name=_('Picture'))
    create_date = models.DateField(auto_now_add=True)
    create = models.DateTimeField(auto_now_add=True)
    timestamp = models.IntegerField(db_index=True, default=1347546432)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    like = models.IntegerField(default=0)
    url = models.CharField(blank=True, max_length=2000,
                           validators=[URLValidator()])
    status = models.IntegerField(default=PENDING, blank=True,
                                 verbose_name=_("Status"),
                                 choices=STATUS_CHOICES)
    device = models.IntegerField(default=DEVICE_WEB, blank=True,
                                 choices=DEVICE_CHOICES)
    hash = models.CharField(max_length=32, blank=True, db_index=True)
    actions = models.IntegerField(default=1, blank=True)
    is_ads = models.BooleanField(default=False, blank=True,
                                 verbose_name=_("Advertisement"))
    view = models.IntegerField(default=0, db_index=True)
    show_in_default = models.BooleanField(default=False, blank=True,
                                          db_index=True,
                                          verbose_name=_("Show in Home"))

    report = models.IntegerField(default=0, db_index=True)
    cnt_comment = models.IntegerField(default=0, blank=True)
    cnt_like = models.IntegerField(default=0, blank=True)

    height = models.IntegerField(default=-1, blank=True)
    width = models.IntegerField(default=-1, blank=True)

    category = models.ForeignKey(Category, default=1,
                                 verbose_name=_('Category'))
    objects = models.Manager()

    data_236 = None
    data_500 = None

    def __unicode__(self):
        return self.text

    def get_pages(self):
        o = []
        text = self.text
        for r in Results.objects.all():
            if r.get_label_text() in text:
                new_url = reverse('pin-result', args=[r.label])
                href = '<a class="wis_btn green_o" href="{}">{}</a>'.\
                    format(new_url, r.get_label_text())
                o.append(href)
        return o

    @classmethod
    def add_to_home(cls, sender, post_id):
        r_server.lrem(cls.HOME_QUEUE_NAME, post_id)
        r_server.rpush(cls.HOME_QUEUE_NAME, post_id)
        Post.objects.filter(pk=post_id).update(show_in_default=True)
        PostCacheLayer(post_id=post_id).show_in_default_change(status=True)
        post = PostCacheLayer(post_id=post_id).get()

        if post:
            from pin.actions import send_notif_bar
            send_notif_bar(user=post['user']['id'], type=5, post=post_id,
                           actor=sender.id)

    @classmethod
    def remove_from_home(cls, post_id):
        r_server.lrem(cls.HOME_QUEUE_NAME, post_id)
        r_server.lrem(settings.HOME_STREAM, post_id)
        Post.objects.filter(pk=post_id).update(show_in_default=False)
        PostCacheLayer(post_id=post_id).show_in_default_change(status=False)

    @classmethod
    def fix_in_home(cls):
        for post_id in r_server.lrange(cls.HOME_QUEUE_NAME, 0, 0):
            r_server.lrem(settings.HOME_STREAM, post_id)
            r_server.lpush(settings.HOME_STREAM, post_id)
            r_server.lrem(cls.HOME_QUEUE_NAME, post_id)

    def get_username(self):
        from cacheLayer import UserDataCache
        return UserDataCache.get_user_name(user_id=self.user_id)

    def get_profile_score(self):
        from user_profile.models import Profile
        score = Profile.objects.only('score').get(user_id=self.user_id)\
            .score
        return score

    def is_pending(self):
        if self.report >= 100:
            return True
        return False

    def get_tags(self):
        hash_tags = re.compile(ur'(?i)(?<=\#)\w+', re.UNICODE)
        tags = hash_tags.findall(self.text)
        all_tags = []
        for tag in tags:
            if tag not in all_tags and len(all_tags) != 4:
                all_tags.append(tag)
        return all_tags

    def save_thumb(self, basewidth):
        ibase = os.path.dirname(self.image)
        ipath = "%s/%s" % (settings.MEDIA_ROOT, self.image)
        idir = os.path.dirname(ipath)
        iname = os.path.basename(ipath)
        img = Image.open(ipath)
        wpercent = (basewidth / float(img.size[0]))
        hsize = int((float(img.size[1]) * float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        w, h = img.size
        nname = "%dx%d_%s" % (w, h, iname)
        npath = "%s/%s" % (idir, nname)
        if not os.path.exists(npath):
            img.save(npath)
        return ibase, nname, h

    def get_image_sizes(self):
        if self.height != -1 and self.width != -1:
            return {
                "width": self.width,
                "height": self.height
            }

        try:
            ipath = "{}/{}".format(settings.MEDIA_ROOT, self.image)
            img = Image.open(ipath)
            Post.objects.filter(id=self.id)\
                .update(height=img.size[1], width=img.size[0])
        except Exception:
            pass
        return {
            "width": self.width,
            "height": self.height
        }

    def clear_cache(self):
        cname = "pmeta_%d_236" % int(self.id)
        cache.delete(cname)
        cname = "pmeta_%d_500" % int(self.id)
        cache.delete(cname)

    def get_image_236(self, api=False):
        if self.data_236:
            return self.data_236
        cname = "pmeta_%d_236" % int(self.id)
        ccache = cache.get(cname)
        ccache = None
        if ccache:
            new_image_url, h = ccache.split(":")
        else:
            try:
                imeta = PostMetaData.objects.only('img_236_h', 'img_236')\
                    .get(post_id=int(self.id))
                if not imeta.img_236_h:
                    raise PostMetaData.DoesNotExist
                new_image_url = imeta.img_236
                h = imeta.img_236_h
                a = [new_image_url, str(h)]
                d = ":".join(a)
                cache.set(cname, d, 86400)
            except PostMetaData.DoesNotExist:
                try:
                    ibase, nname, h = self.save_thumb(basewidth=236)
                except IOError:
                    return False
                except Exception:
                    return False
                new_image_url = ibase + "/" + nname
                try:
                    p, created = PostMetaData.objects\
                        .get_or_create(post_id=self.id)

                    if not p.img_236_h:
                        p.img_236 = new_image_url
                        p.img_236_h = h
                        p.save()
                except:
                    pass

        if api:
            final_url = new_image_url
        else:
            final_url = settings.MEDIA_PREFIX + "/media/" + new_image_url
        data = {
            'url': final_url,
            'h': int(h),
            'hw': "%dx%d" % (int(h), 236)
        }
        self.data_236 = data

        return data

    def get_image_500(self, api=False):
        if self.data_500:
            return self.data_500
        cname = "pmeta_%d_500" % int(self.id)
        ccache = cache.get(cname)
        ccache = None
        if ccache:
            new_image_url, h = ccache.split(":")
        else:

            try:
                imeta = PostMetaData.objects.only('img_500_h', 'img_500')\
                    .get(post_id=int(self.id))
                if not imeta.img_500_h:
                    raise PostMetaData.DoesNotExist
                new_image_url = imeta.img_500
                h = imeta.img_500_h

                a = [new_image_url, str(h)]
                d = ":".join(a)
                cache.set(cname, d, 86400)

            except PostMetaData.DoesNotExist:
                try:
                    ibase, nname, h = self.save_thumb(basewidth=500)
                except IOError:
                    return False
                except Exception:
                    return False

                new_image_url = ibase + "/" + nname
                try:
                    p, created = PostMetaData.objects\
                        .get_or_create(post_id=self.id)
                    if not p.img_500_h:
                        p.img_500 = new_image_url
                        p.img_500_h = h
                        p.save()
                except:
                    pass

            except Exception:
                pass

        if api:
            final_url = new_image_url
        else:
            final_url = settings.MEDIA_PREFIX + "/media/" + new_image_url
        data = {
            'url': final_url,
            'h': int(h),
            'hw': "{}x{}".format(int(h), 500)
        }
        self.data_500 = data

        return data

    def md5_for_file(self, f, block_size=2 ** 20):
        md5 = hashlib.md5()
        while True:
            data = f.read(block_size)
            if not data:
                break
            md5.update(data)
        return md5.hexdigest()

    def delete(self, *args, **kwargs):
        if self.report > 9:
            from pin.tasks import porn_feedback
            porn_feedback.delay(post_image=self.get_image_500()['url'],
                                status='pos')
        try:
            delete_image.delay(self.image)
            delete_image.delay(self.postmetadata.img_500)
            self.move_file()
        except Exception, e:
            print str(e)
            pass

        from user_profile.models import Profile
        n_score = 10 * self.cnt_like
        Profile.objects.filter(user_id=self.user_id)\
            .update(cnt_post=F('cnt_post') - 1, score=F('score') - n_score)

        from models_redis import LikesRedis
        LikesRedis(post_id=self.id).delete_likes()

        MonthlyStats.log_hit(MonthlyStats.DELETE_POST)

        cs = CatStreams()
        cs.remove_post(self.category_id, self.id)

        post_id = self.id
        super(Post, self).delete(*args, **kwargs)

        # Delete post from elastic
        ps = ESPosts()
        ps.delete(post_id=post_id)

        # Delete post from cache
        if settings.TUNING_CACHE:
            PostCacheLayer(post_id=post_id).delete()

    def move_file(self):
        path = self.postmetadata.img_236

        if path:
            slices = path.split("/")
            server_name = slices[1]
            filename = slices[-1]
            storage = None
            try:
                storage = Storages.objects.get(name=server_name)
            except Exception, e:
                str(e)

            if storage:
                src = "{}/{}".format(storage.path, path)
                dest_folder = "{}/removed_image".format(storage.path)
                dest = "{}/{}".format(dest_folder, filename)
                if not os.path.exists(dest_folder):
                    os.makedirs(dest_folder)
                os.rename(src, dest)

    def get_removed_image_path(self):
        path = self.postmetadata.img_236
        url = ""
        if path:
            slices = path.split("/")
            filename = slices[-1]
            server_name = slices[1]

            folder_path = "/mnt/wisgoon/{}/removed_image/".format(server_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

            url = "{}/media/removed/{}/{}"\
                .format(settings.MEDIA_PREFIX, server_name, filename)
        return url

    def date_lt(self, date, how_many_days=15):
        lt_date = datetime.now() - timedelta(days=how_many_days)
        lt_timestamp = mktime(lt_date.timetuple())
        timestamp = mktime(date.timetuple())
        return timestamp < lt_timestamp

    @classmethod
    def hot(cls, post_id, amount=1):
        hotest = r_server.smembers('hottest')
        if str(post_id) not in hotest:
            r_server.zincrby('hot', int(post_id), amount=1)

        r_server.zremrangebyrank('hot', 0, -1001)

    @classmethod
    def get_hot(cls, values=False):
        h = r_server.zrange('hot', 0, 0, withscores=True, desc=True)
        if h[0][1] > 110:
            r_server.sadd('hottest', h[0][0])
            r_server.zincrby('hot', h[0][0], amount=-100)

        if h[0][1] <= 49:
            return False

        if values:
            post = Post.objects\
                .values(*cls.NEED_KEYS)\
                .filter(id=h[0][0])
        else:
            post = Post.objects.filter(id=h[0][0])

        if not post:
            r_server.zrem('hot', h[0][0])
        return post

    @classmethod
    def add_to_stream(cls, post):
        if not post.accept_for_stream() or post.user.profile.is_private:
            return
        latest_stream = settings.STREAM_LATEST
        r_server.lrem(latest_stream, post.id)
        r_server.lpush(latest_stream, post.id)

        cat_stream = "{}_{}"\
            .format(settings.STREAM_LATEST_CAT, post.category_id)
        r_server.lrem(cat_stream, post.id)
        r_server.lpush(cat_stream, post.id)

        r_server.ltrim(cat_stream, 0, settings.LIST_LONG)
        r_server.ltrim(latest_stream, 0, settings.LIST_LONG)

        stream = CatStreams()
        stream.add_post(post.category_id,
                        post.id,
                        post.user_id,
                        post.timestamp)

    @classmethod
    def set_stream_to_redis(cls, user_id):
        pass
        # user_stream = "%s_%d" % (settings.USER_STREAM, int(user_id))
        # s = Stream.objects.filter(user_id=user_id)\
        #     .values_list('post_id', flat=True).order_by('-id')[:1000]
        # for ss in s:
        #     r_server.rpush(user_stream, ss)

    @classmethod
    def add_to_user_stream(cls, post_id, user_id, post_owner):
        from pin.models_stream import RedisUserStream
        rus = RedisUserStream()
        rus.add_post([user_id], post_id, post_owner)
        # user_stream = "%s_%d" % (settings.USER_STREAM, int(user_id))

        # r_server.lrem(user_stream, post_id)
        # r_server.lpush(user_stream, post_id)
        # r_server.ltrim(user_stream, 0, 1000)

        # print "add to stream {}".format(user_id)
        # us = UserStream()
        # us.add_post(user_id, post_id, post_owner)

    @classmethod
    def add_to_users_stream(cls, post_id, user_ids, post_owner):
        from pin.models_stream import RedisUserStream
        rus = RedisUserStream()
        rus.add_post(user_ids, post_id, post_owner)
        # user_stream = "%s_%d" % (settings.USER_STREAM, int(user_id))

        # r_server.lrem(user_stream, post_id)
        # r_server.lpush(user_stream, post_id)
        # r_server.ltrim(user_stream, 0, 1000)

        # print "add to stream {}".format(user_id)
        # us = UserStream()
        # us.add_post_batch(user_ids, post_id, post_owner)

    @classmethod
    def remove_post_from_stream(cls, user_id, post_id):
        pass
        # user_stream = "%s_%d" % (settings.USER_STREAM, int(user_id))
        # r_server.lrem(user_stream, post_id)

    @classmethod
    def add_to_set(cls, set_name, post, set_cat=True):
        r_server.zadd(set_name, int(post.timestamp), post.id)
        r_server.zremrangebyrank(set_name, 0, -1001)

        if set_cat:
            cat_set_key = "post_latest_%s" % post.category.id
            r_server.zadd(cat_set_key, int(post.timestamp), post.id)
            r_server.zremrangebyrank(cat_set_key, 0, -1001)

    def hash_exists(self):
        lname = "duplic"
        r_dup = r_server.lrange(lname, 0, 100)
        if self.hash in r_dup:
            return True

        r_server.lpush(lname, self.hash)
        r_server.ltrim(lname, 0, 101)

        return False

    def accept_for_stream(self):
        file_path = os.path.join(settings.MEDIA_ROOT, self.image)
        if os.path.exists(file_path):
            try:
                img = Image.open(file_path)
                if img.size[0] < 236:
                    return False
            except:
                pass

        return True

    def save(self, *args, **kwargs):
        from user_profile.models import Profile
        try:
            profile = Profile.objects.get(user=self.user)

            if profile.score > settings.SCORE_FOR_STREAMS:
                self.status = 1

        except Profile.DoesNotExist:
            pass

        file_path = os.path.join(settings.MEDIA_ROOT, self.image)
        if os.path.exists(file_path):

            image_file = open(file_path)
            self.hash = self.md5_for_file(image_file)
            if not settings.DEBUG:
                if self.hash_exists():
                    self.status = 0

            if not self.accept_for_stream():
                self.status = 0

            if Official.objects.filter(user=self.user).count():
                self.status = 1

        self.text = emoji.demojize(self.text)
        self.text = normalize_tags(self.text)
        super(Post, self).save(*args, **kwargs)
        if settings.TUNING_CACHE:
            try:
                PostCacheLayer(post_id=self.id).post_change(self)
            except:
                pass

    @models.permalink
    def get_absolute_url(self):
        return ('pin-item', [str(self.id)])

    def get_web_absolute_url(self):
        from pin.api_tools import abs_url

        return abs_url(reverse("pin-item",
                               kwargs={"item_id": self.id}),
                       api=False)

    def get_user_url(self):
        url = '/pin/user/{}'.format(str(self.user_id))
        return '<a href="{}" target="_blank">{}</a>'.format(url, self.user)
    get_user_url.allow_tags = True

    def get_host_url(self):
        abs = self.get_absolute_url()

        if settings.DEBUG:
            return abs
        else:
            host_url = 'http://%s%s' % (Site.objects.get_current().domain, abs)
            return host_url

    def get_image_absolute_url(self):
        if settings.DEBUG:
            url = '%s%s' % (settings.MEDIA_URL, self.image)
        else:
            url = 'http://%s%s%s' % (Site.objects.get_current().domain,
                                     settings.MEDIA_URL, self.image)
        return url

    def get_image_thumb(self):
        try:
            im = get_thumbnail(self.image, '192')
        except:
            im = None
        return im

    @classmethod
    def change_tag_slug(cls, sender, instance, *args, **kwargs):
        if kwargs['created']:
            tag = instance
            tag.slug = '-'.join(tag.name.split())
            tag.save()

    def admin_image(self):
        img = self.get_image_236()
        if img:
            return """
                <a href="/media/%s" target="_blank"><img src="%s" /></a>
            """ % (self.image, img['url'])
        return 'None'
    admin_image.allow_tags = True

    def cnt_likes(self):
        return self.cnt_like

        cnt = Likes.objects.filter(post_id=self.id).count()
        Post.objects.filter(pk=self.id).update(cnt_like=cnt)
        return cnt

    def cnt_comments(self):
        if self.cnt_comment == -1:
            cnt = Comments.objects.filter(object_pk_id=self.id).count()
            Post.objects.filter(pk=self.id).update(cnt_comment=cnt)
        else:
            cnt = self.cnt_comment

        return cnt

    def approve(self):
        from tasks import send_notif_bar

        Post.objects.filter(pk=self.id)\
            .update(status=self.APPROVED, timestamp=time.time())

        if self.status == self.PENDING:
            Post.add_to_stream(post=self)

        r_server.srem('pending_photos', self.id)

        send_notif_bar(user=self.user.id, type=3, post=self.id,
                       actor=self.user.id)

    @classmethod
    def home_latest(cls, pid=0, limit=20):
        home_stream = settings.HOME_STREAM

        if not r_server.exists(home_stream):
            hposts = Post.objects.values_list('id', flat=True)\
                .filter(show_in_default=1).order_by('-timestamp')[:5000]
            if hposts:
                r_server.rpush(home_stream, *hposts)

        if pid == 0:
            pl = r_server.lrange(home_stream, 0, limit)
            return pl[:limit]

        pl = r_server.lrange(home_stream, 0, settings.LIST_LONG)

        if pid:
            try:
                pid_index = pl.index(str(pid))
                idis = pl[pid_index + 1: pid_index + limit + 1]
                return idis
            except ValueError:
                return []

        return []

    @classmethod
    def home_queue(cls, pid=0, limit=20):
        home_stream = cls.HOME_QUEUE_NAME

        pl = r_server.lrange(home_stream, 0, settings.LIST_LONG)
        pl.reverse()

        if pid == 0:
            # pl = r_server.lrange(home_stream, 0, limit)
            return pl[:limit]

        if pid:
            try:
                pid_index = pl.index(str(pid))
                idis = pl[pid_index + 1: pid_index + limit + 1]
                return idis
            except ValueError:
                return []

        return []

    @classmethod
    def latest(cls, pid=0, cat_id=0, limit=20):
        return cls.latest_cat(pid, cat_id, limit)

        if cat_id:
            return cls.latest_cat(pid, cat_id, limit)
        else:
            cat_stream = settings.STREAM_LATEST

        if pid == 0:
            pl = r_server.lrange(cat_stream, 0, limit)
        else:
            cache_name = "cl_{}_{}:{}".format(cat_stream, pid, limit)
            cache_data = cache.get(cache_name)
            if cache_data:
                return cache_data
            pl = r_server.lrange(cat_stream, 0, -1)

        if pid == 0:
            return pl[:limit]

        if pid:
            try:
                pid_index = pl.index(str(pid))
                idis = pl[pid_index + 1: pid_index + limit + 1]
                cache.set(cache_name, idis, 86400)
                return idis
            except ValueError:
                return []

        return []

    @classmethod
    def latest_cat(cls, pid=0, cat_id=0, limit=20):
        cs = CatStreams()
        return cs.get_posts(cat_id, pid)
        # return []

    @classmethod
    def last_likes(cls):
        pl = r_server.lrange(settings.LAST_LIKES, 0, 30)
        return pl[:30]

    @classmethod
    def user_stream_latest(cls, user_id, pid=0):
        rus = RedisUserStream()
        pl = rus.get_stream_posts(user_id, pid)
        return pl

        # us = UserStream()
        # pl = us.get_posts(user_id, pid)
        # return pl

        # row_per_page = 20
        # if not user_id:
        #     return []
        # user_stream = "{}_{}".format(settings.USER_STREAM, int(user_id))
        # pl = r_server.lrange(user_stream, 0, 1000)
        # if not pl:
        #     Post.set_stream_to_redis(user_id=user_id)
        #     pl = r_server.lrange(user_stream, 0, 1000)

        # if pid == 0:
        #     import collections
        #     dups = [x for x, y in collections.Counter(pl).items() if y > 1]

        #     for dup in dups:
        #         r_server.lrem(user_stream, dup)

        #     return pl[:row_per_page]

        # if pid:
        #     try:
        #         pid_index = pl.index(str(pid))
        #         idis = pl[pid_index + 1: pid_index + row_per_page]
        #         return idis
        #     except:
        #         return []

        # return []


class Bills2(models.Model):
    COMPLETED = 1
    UNCOMPLETED = 0
    FAKERY = 2
    VALIDATE_ERROR = 3
    NOT_VALID = 4

    STATUS_CHOICES = (
        (COMPLETED, _('Completed')),
        (UNCOMPLETED, _('Uncompleted')),
        (FAKERY, _('Fakery')),
        (VALIDATE_ERROR, _('validate error')),
        (NOT_VALID, _('not valid')),
    )

    status = models.IntegerField(blank=True, null=True, default=0,
                                 choices=STATUS_CHOICES)
    amount = models.IntegerField(blank=True, null=True)
    trans_id = models.CharField(max_length=250, blank=True,
                                null=True, db_index=True)

    create_date = models.DateField(default=datetime.now)
    create_time = models.DateTimeField(default=datetime.now)

    user = models.ForeignKey(settings.AUTH_USER_MODEL)


class Follow(models.Model):
    follower = models.ForeignKey(settings.AUTH_USER_MODEL,
                                 related_name='follower')
    following = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='following')

    @classmethod
    def get_follow_status(cls, follower, following):
        fstatus = Follow.objects.filter(follower_id=follower,
                                        following_id=following).exists()
        return fstatus

    def delete(self, *args, **kwargs):
        from user_profile.models import Profile
        follower_id = self.follower.id
        following_id = self.following.id

        Profile.objects.filter(user_id=follower_id)\
            .update(cnt_following=F('cnt_following') - 1)

        Profile.objects.filter(user_id=following_id)\
            .update(cnt_followers=F('cnt_followers') - 1)

        MonthlyStats.log_hit(MonthlyStats.UNFOLLOW)

        FollowUser.delete_relations(self.follower,
                                    self.following)
        super(Follow, self).delete(*args, **kwargs)

        # TO DO
        # from pin.tasks import remove_from_stream
        # remove_from_stream.delay(user_id=follower_id, owner_id=following_id)

        from models_casper import Notification
        # us = UserStream()
        notif = Notification()
        notif.update_notif(a_user_id=following_id,
                           a_type=10,
                           a_actor=follower_id,
                           a_object_id=None)

        # decrement_cnt_notif on redis
        from models_redis import NotificationRedis
        NotificationRedis(user_id=following_id).decrement_cnt_notif()

        # us.unfollow(follower_id, following_id)
        # remove_from_stream(user_id=following_id, owner_id=follower_id)

        from models_stream import RedisUserStream
        rus = RedisUserStream()
        rus.unfollow(follower_id, following_id)

    def save(self, *args, **kwargs):
        super(Follow, self).save(*args, **kwargs)

    @classmethod
    def new_follow(cls, sender, instance, *args, **kwargs):
        if kwargs['created']:
            from user_profile.models import Profile
            follower_id = instance.follower.id
            following_id = instance.following.id

            # Delete follow request
            FollowRequest.objects.filter(user_id=follower_id,
                                         target_id=following_id).delete()

            # Update cnt_following and cnt_follower
            Profile.objects.filter(user_id=follower_id)\
                .update(cnt_following=F('cnt_following') + 1)

            Profile.objects.filter(user_id=following_id)\
                .update(cnt_followers=F('cnt_followers') + 1)

            # Send notification
            from pin.actions import send_notif_bar
            send_notif_bar(user=instance.following.id,
                           type=10,
                           post=None,
                           actor=instance.follower.id)

            # Monthly follow log
            MonthlyStats.log_hit(MonthlyStats.FOLLOW)

            # Neo4j graph
            FollowUser.get_or_create(instance.follower,
                                     instance.following,
                                     "follow")

            # Add following posts to follower stream
            # from models_casper import UserStream
            # us = UserStream()
            pid_list = Post.objects.filter(user_id=following_id)\
                .only("id")\
                .values_list("id", flat=True)\
                .order_by("-id")[:100]

            # us.follow(follower_id, pid_list, following_id)

            from models_stream import RedisUserStream
            rus = RedisUserStream()
            rus.follow(follower_id, pid_list, following_id)


class Stream(models.Model):
    following = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  related_name='stream_following')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user')
    post = models.ForeignKey(Post)
    date = models.IntegerField(default=0)

    class Meta:
        unique_together = (("following", "user", "post"),)

    @classmethod
    def add_post(cls, sender, instance, *args, **kwargs):
        post = instance
        post.get_image_236()
        post.get_image_500()
        post.get_image_sizes()
        if kwargs['created']:
            from pin.tasks import add_to_storage
            add_to_storage.delay(post_id=post.id)

            MonthlyStats.log_hit(object_type=MonthlyStats.POST)

            from user_profile.models import Profile
            Profile.objects.filter(user_id=post.user_id)\
                .update(cnt_post=F('cnt_post') + 1)

            user = post.user

            Post.add_to_user_stream(post_id=post.id, user_id=user.id,
                                    post_owner=user.id)

            from pin.tasks import post_to_followers
            post_to_followers.delay(user_id=user.id, post_id=post.id)

            if post.status == Post.APPROVED and post.accept_for_stream():
                Post.add_to_stream(post=post)

            # Add to elastic
            ps = ESPosts()
            ps.save(post_obj=instance)


class Likes(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='pin_post_user_like')
    post = models.ForeignKey(Post, related_name="post_item")
    ip = models.GenericIPAddressField(default='127.0.0.1')

    class Meta:
        unique_together = (("post", "user"),)

    def save(self, *args, **kwargs):
        super(Likes, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        from user_profile.models import Profile

        u_last_likes = "%s_%d" % (settings.USER_LAST_LIKES, int(self.user.id))
        r_server.lrem(u_last_likes, self.post.id)

        Post.objects.filter(pk=self.post.id).update(cnt_like=F('cnt_like') - 1)

        Profile.after_dislike(user_id=self.post.user_id)

        key_str = "%s_%d" % (settings.POST_LIKERS, self.post.id)
        r_server.srem(key_str, int(self.user.id))

        super(Likes, self).delete(*args, **kwargs)

    @classmethod
    def user_like_post(cls, sender, instance, *args, **kwargs):
        from user_profile.models import Profile

        MonthlyStats.log_hit(object_type=MonthlyStats.LIKE)

        like = instance
        post = like.post
        # sender = like.user

        Post.objects.filter(pk=post.id).update(cnt_like=F('cnt_like') + 1)

        r_server.lrem(settings.LAST_LIKES, post.id)
        r_server.lpush(settings.LAST_LIKES, post.id)
        r_server.ltrim(settings.LAST_LIKES, 0, 1000)

        u_last_likes = "%s_%d" % (settings.USER_LAST_LIKES, int(like.user.id))
        if not r_server.exists(u_last_likes):
            likes = Likes.objects.values_list('post_id', flat=True)\
                .filter(user_id=like.user.id).order_by('-id')[:1000]
            r_server.rpush(u_last_likes, *likes)
        else:
            r_server.lrem(u_last_likes, post.id)
            r_server.lpush(u_last_likes, post.id)
            r_server.ltrim(u_last_likes, 0, 1000)

        Profile.after_like(user_id=post.user_id)

        key_str = "%s_%d" % (settings.POST_LIKERS, post.id)
        r_server.sadd(key_str, int(like.user.id))
        r_server.expire(key_str, 86400)

        hcpstr = "like_max_%d" % post.id
        cp = cache.get(hcpstr)
        if cp:
            hstr = "like_cache_%s%s" % (post.id, cp)
            cache.delete(hstr)

        str_likers = "web_likes_%s" % post.id
        cache.delete(str_likers)

        # from pin.actions import send_notif_bar

        # send_notif_bar(user=post.user_id, type=1, post=post.id,
        #                actor=sender.id)

    @classmethod
    def user_likes(cls, user_id, pid=0):
        user_last_likes = "%s_%d" % (settings.USER_LAST_LIKES, int(user_id))

        pl = r_server4.lrange(user_last_likes, 0, 1000)
        if pid:
            try:
                pid_index = pl.index(str(pid))
            except ValueError:
                return []
            idis = pl[pid_index + 1: pid_index + 20]
            return idis

        return pl[:20]

    @classmethod
    def user_in_likers(cls, post_id, user_id):
        from models_redis import LikesRedis
        return LikesRedis(post_id=post_id).user_liked(user_id=user_id)

        key_str = "{}_{}".format(settings.POST_LIKERS, post_id)

        if r_server.sismember(key_str, str(user_id)):
            return True

        if not r_server.exists(key_str):
            post_likers = Likes.objects.values_list('user_id', flat=True)\
                .filter(post_id=post_id)

            if post_likers:
                r_server.sadd(key_str, *post_likers)
                r_server.expire(key_str, 86400)

                if user_id in post_likers:
                    return True
            else:
                r_server.sadd(key_str, int(-1))

            if user_id in post_likers:
                return True

        return False


class Notifbar(models.Model):
    LIKE = 1
    COMMENT = 2
    APPROVE = 3
    FAULT = 4
    TYPES = (
        (LIKE, _('like')),
        (COMMENT, _('comment')),
        (APPROVE, _('approve')),
        (FAULT, _('fault'))
    )

    post = models.ForeignKey(Post)
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name="actor_id")
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name="post_user_id")
    seen = models.BooleanField(default=False)
    type = models.IntegerField(default=1, choices=TYPES)
    date = models.DateTimeField(auto_now_add=True)


class Notif(models.Model):
    LIKE = 1
    COMMENT = 2
    APPROVE = 3
    FAULT = 4
    TYPES = (
        (LIKE, _('like')),
        (COMMENT, _('comment')),
        (APPROVE, _('approve')),
        (FAULT, _('fault'))
    )

    post = models.ForeignKey(Post)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_id")
    text = models.CharField(max_length=500)
    seen = models.BooleanField(default=False)
    type = models.IntegerField(default=1, choices=TYPES)
    date = models.DateTimeField(auto_now_add=True)


class Notif_actors(models.Model):
    notif = models.ForeignKey(Notif, related_name="notif")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="actor")


class App_data(models.Model):
    name = models.CharField(max_length=250)
    file = models.FileField(upload_to='app')
    version = models.CharField(max_length=50)
    version_code = models.IntegerField(default=0, blank=True)
    current = models.BooleanField(default=1)


class Comments(models.Model):
    BAD_WORDS = [
        u'7108',
        u"لعنت الله",
        u"ملعونین",
        u"حرومزاده",
        u"اعتبار رایگان",
        u"پیامک کن",
        u"شارژ رایگان",
        u"شارژ مجانی",
        u"اعتبار مجانی",
    ]

    NEED_KEYS_API = ['object_pk', 'submit_date', 'comment', 'user', 'score']

    comment = models.TextField()
    submit_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(default='127.0.0.1',
                                              db_index=True)
    is_public = models.BooleanField(default=False, db_index=True)
    reported = models.BooleanField(default=False, db_index=True)

    object_pk = models.ForeignKey(Post, related_name='comment_post')
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='comment_sender')
    score = models.IntegerField(default=0, blank=True, )

    def __unicode__(self):
        return self.comment

    def get_username(self):
        from cacheLayer import UserDataCache
        return UserDataCache.get_user_name(user_id=self.user_id)

    def date_lt(self, date, how_many_days=15):
        lt_date = datetime.now() - timedelta(days=how_many_days)
        lt_timestamp = mktime(lt_date.timetuple())
        timestamp = mktime(date.timetuple())
        return timestamp < lt_timestamp

    def save(self, *args, **kwargs):
        # if Block.objects.filter(user_id=self.object_pk.user_id,
        #                         blocked_id=self.user_id).exists():
        #     return

        if not self.pk:
            Post.objects.filter(pk=self.object_pk_id)\
                .update(cnt_comment=F('cnt_comment') + 1)

            # Elastic update
            ps = ESPosts()
            ps.inc_cnt_comment(post_id=self.object_pk_id)

        # self.comment = emoji.demojize(self.comment)[:2048]
        self.comment = emoji.demojize(self.comment[:2048])

        comment_cache_name = "com_{}".format(int(self.object_pk_id))
        cache.delete(comment_cache_name)
        super(Comments, self).save(*args, **kwargs)

        # from models_casper import PostComments
        # PostComments.objects.create(post_id=self.object_pk_id,
        #                             create_time=time.time(),
        #                             comment=self.comment,
        #                             ip_address=self.ip_address,
        #                             user_id=self.user_id)

        if settings.TUNING_CACHE:
            PostCacheLayer(post_id=self.object_pk.id)\
                .comment_change(self.object_pk.cnt_comment)

    @classmethod
    def add_comment(cls, sender, instance, created, *args, **kwargs):
        from pin.actions import send_notif_bar
        from pin.tools import get_post_user_cache
        from pin.model_mongo import Notif

        if not created:
            return None

        MonthlyStats.log_hit(object_type=MonthlyStats.COMMENT)

        comment = instance
        post = get_post_user_cache(post_id=comment.object_pk_id)
        actors_list = []

        # Push notif for post owner
        if comment.user_id != post.user.id:
            send_notif_bar(user=post.user.id, type=Notif.COMMENT, post=post.id,
                           actor=comment.user.id, comment=comment)

            actors_list.append(post.user.id)

        # Wisgoon account
        if post.user.id == 11253:
            return

        # Push notif for user metioned
        mention = re.compile("(?:^|\s)[＠ @]{1}([^\s#<>[\]|{}]+)", re.UNICODE)
        mentions = mention.findall(comment.comment)
        if mentions:
            for username in mentions:
                try:
                    u = User.objects.only('id').get(username=username)
                except User.DoesNotExist:
                    continue
                if u.id != comment.user_id and u.id != post.user.id:
                    send_notif_bar(user=u.id, type=Notif.COMMENT, post=post.id,
                                   actor=comment.user_id,
                                   comment=comment)
            return

    def delete(self, *args, **kwargs):
        from pin.models_casper import Notification

        Post.objects.filter(pk=self.object_pk.id)\
            .update(cnt_comment=F('cnt_comment') - 1)

        comment_cache_name = "com_%d" % self.object_pk.id
        cache.delete(comment_cache_name)
        comment_id = self.id
        super(Comments, self).delete(*args, **kwargs)

        """ Get mention user id """
        actors_list = [self.object_pk.user_id]
        mention = re.compile("(?:^|\s)[＠ @]{1}([^\s#<>[\]|{}]+)", re.UNICODE)
        mentions = mention.findall(self.comment)
        if mentions:
            for username in mentions:
                try:
                    u = User.objects.only('id').get(username=username)
                except User.DoesNotExist:
                    continue
                if u.id != self.user_id and u.id != self.object_pk.user_id:
                    actors_list.append(u.id)

        """ Remove notification from cassandra """
        for user_id in actors_list:
            notif = Notification()
            notif.remove_comment_notif(a_user_id=user_id,
                                       comment_id=comment_id)

        if settings.TUNING_CACHE:
            post_id = self.object_pk_id
            PostCacheLayer(post_id=post_id)\
                .delete_comment(self.object_pk.cnt_comment)

        # Elastic update
        ps = ESPosts()
        ps.decr_cnt_comment(post_id=self.object_pk_id)

    @models.permalink
    def get_absolute_url(self):
        return ('pin-item', [str(self.object_pk_id)])

    def admin_link(self):
        u = self.get_absolute_url()
        return '<a href="{}" target="_blank">{}</a>'.format(u, _('Seeing'))

    admin_link.allow_tags = True


class Comments_score(models.Model):
    comment = models.ForeignKey(Comments)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='comment_like_user')
    score = models.IntegerField(default=0, blank=True)


class Report(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='report_user')
    post = models.ForeignKey(Post, related_name='report_post')

    class Meta:
        unique_together = (("post", "user"),)


class Block(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='blocker')
    blocked = models.ForeignKey(settings.AUTH_USER_MODEL,
                                related_name='blocked')

    @classmethod
    def block_user(cls, user_id, blocked_id):
        if user_id == blocked_id:
            return False

        try:
            Block.objects.get_or_create(user_id=user_id, blocked_id=blocked_id)
            MonthlyStats.log_hit(MonthlyStats.BLOCK)
            follows = Follow.objects.filter(Q(following_id=user_id,
                                              follower_id=blocked_id) |
                                            Q(following_id=blocked_id,
                                              follower_id=user_id))

            for follow in follows:
                follow.delete()
        except:
            pass

        return True

    @classmethod
    def unblock_user(cls, user_id, blocked_id):
        if user_id == blocked_id:
            return False
        MonthlyStats.log_hit(MonthlyStats.UNBLOCK)
        Block.objects.filter(user_id=user_id, blocked_id=blocked_id).delete()


class PhoneData(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="phone",
                                null=True, blank=True)
    imei = models.CharField(max_length=50)
    os = models.CharField(max_length=50)
    phone_model = models.CharField(max_length=50)
    phone_serial = models.CharField(max_length=50)
    android_version = models.CharField(max_length=20)
    app_version = models.CharField(max_length=10)
    google_token = models.CharField(max_length=500)

    logged_out = models.BooleanField(default=False)
    hash_data = models.CharField(max_length=32, default="")
    extra_data = models.TextField(null=True, blank=True)

    def get_need_fields(self):
        fields = self._meta.get_all_field_names()
        try:
            fields.remove(u'id')
            fields.remove('hash_data')
            fields.remove('logged_out')
        except:
            pass
        return fields

    def get_hash_data(self):
        h_str = ""
        fields = self.get_need_fields()

        h_str = '%'.join([str(getattr(self, f)) for f in fields])

        self.hash_data = hashlib.md5(h_str).hexdigest()
        return self.hash_data

    def save(self, *args, **kwargs):
        super(PhoneData, self).save(*args, **kwargs)


class InstaAccount(models.Model):
    insta_id = models.BigIntegerField()
    cat = models.ForeignKey(Category)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    lc = models.DateTimeField(auto_now=True)


class PostMetaData(models.Model):
    CREATED = 1
    FULL_IMAGE_CREATE = 2
    ERROR_IN_ORIGINAL = 3
    REDIS_CHANGE_SERVER = 4

    STATUS = (
        (CREATED, _('created')),
        (FULL_IMAGE_CREATE, _('full image create')),
        (ERROR_IN_ORIGINAL, _('error in original image')),
        (REDIS_CHANGE_SERVER, 'redis server change'),
    )

    post = models.OneToOneField(Post)
    original_size = models.IntegerField(default=0)
    status = models.IntegerField(default=CREATED, choices=STATUS,
                                 db_index=True)
    img_236_h = models.IntegerField(default=0)
    img_500_h = models.IntegerField(default=0)
    img_236 = models.CharField(max_length=250)
    img_500 = models.CharField(max_length=250)


class BannedImei(models.Model):
    imei = models.CharField(max_length=50, db_index=True)
    create_time = models.DateTimeField(auto_now=True)
    description = models.TextField(default="")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, default=1)


class Log(models.Model):
    POST = 1
    COMMENT = 2
    USER = 3
    COMMENT_TEST = 4

    TYPES = (
        (POST, _("post")),
        (COMMENT, _("comment")),
        (USER, _("user")),
        (COMMENT_TEST, _("comment test")),
    )

    DELETE = 1
    PENDING = 2
    BAD_COMMENT = 3
    BAD_POST = 4
    BAN_IMEI = 5
    BAN_ADMIN = 6
    ACTIVE_USER = 7
    DEACTIVE_USER = 8
    BAN_PROFILE = 9
    UNBAN_PROFILE = 10
    UNBAN_IMEI = 11
    UPDATE_PROFILE = 12

    ACTIONS = (
        (DELETE, _("delete")),
        (PENDING, _("pending")),
        (BAD_COMMENT, _("bad comment")),
        (BAD_POST, _("bad post")),
        (BAN_IMEI, _("ban imei")),
        (BAN_ADMIN, _("ban by admin")),
        (DEACTIVE_USER, _("Deactive user")),
        (ACTIVE_USER, _("activated")),
        (BAN_PROFILE, _("ban profile")),
        (UNBAN_PROFILE, _("unban profile")),
        (UPDATE_PROFILE, _("update profile"))
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    action = models.IntegerField(default=1, choices=ACTIONS, db_index=True)
    object_id = models.IntegerField(default=0, db_index=True)
    content_type = models.IntegerField(default=1, choices=TYPES, db_index=True)
    ip_address = models.GenericIPAddressField(default='127.0.0.1',
                                              db_index=True)
    owner = models.IntegerField(default=0)
    text = models.TextField(default="", blank=True, null=True)

    create_time = models.DateTimeField(auto_now=True)

    post_image = models.CharField(max_length=250, blank=True, null=True)

    @classmethod
    def post_delete(cls, post, actor, ip_address="127.0.0.1"):
        try:
            # img_url = post.get_image_236()["url"]
            img_url = post.get_removed_image_path()
        except:
            img_url = ""
        Log.objects.create(user_id=actor.id,
                           action=1,
                           object_id=post.id,
                           content_type=1,
                           owner=post.user.id,
                           post_image=img_url,
                           ip_address=ip_address,
                           text=post.text,
                           )

    @classmethod
    def bad_comment(cls, post, actor, ip_address="127.0.0.1", text=""):
        Log.objects.create(user_id=actor.id,
                           action=3,
                           object_id=post.id,
                           content_type=2,
                           owner=post.user.id,
                           ip_address=ip_address,
                           text=text,
                           )

    @classmethod
    def bad_comment_test(cls, post, actor, ip_address="127.0.0.1", text=""):
        Log.objects.create(user_id=actor.id,
                           action=3,
                           object_id=post.id,
                           content_type=Log.COMMENT_TEST,
                           owner=post.user.id,
                           ip_address=ip_address,
                           text=text,
                           )

    @classmethod
    def bad_post(cls, actor, text=""):
        Log.objects.create(user_id=actor.id,
                           action=4,
                           content_type=1,
                           text=text,
                           )

    @classmethod
    def ban_by_admin(cls, actor, user_id, text="", ip_address="127.0.0.1"):
        Log.objects.create(user=actor,
                           action=cls.BAN_ADMIN,
                           content_type=cls.USER,
                           object_id=user_id,
                           text=text,
                           ip_address=ip_address)

    @classmethod
    def ban_by_imei(cls, actor, text="", ip_address="127.0.0.1"):
        Log.objects.create(user=actor,
                           action=cls.BAN_IMEI,
                           content_type=cls.USER,
                           text=text,
                           ip_address=ip_address)

    @classmethod
    def unban_by_imei(cls, actor, text="", ip_address="127.0.0.1"):
        Log.objects.create(user=actor,
                           action=cls.UNBAN_IMEI,
                           content_type=cls.USER,
                           text=text,
                           ip_address=ip_address)

    @classmethod
    def active_user(cls, actor, user_id, text="", ip_address="127.0.0.1"):
        Log.objects.create(user=actor,
                           action=cls.ACTIVE_USER,
                           object_id=user_id,
                           content_type=cls.USER,
                           text=text,
                           ip_address=ip_address)

    @classmethod
    def deactive_user(cls, actor, user_id, text="", ip_address="127.0.0.1"):
        Log.objects.create(user=actor,
                           action=cls.DEACTIVE_USER,
                           object_id=user_id,
                           content_type=cls.USER,
                           text=text,
                           ip_address=ip_address)

    @classmethod
    def ban_profile(cls, actor, user_id, text="", ip_address="127.0.0.1"):
        Log.objects.create(user=actor,
                           action=cls.BAN_PROFILE,
                           object_id=user_id,
                           content_type=cls.USER,
                           text=text,
                           ip_address=ip_address)

    @classmethod
    def unban_profile(cls, actor, user_id, text="", ip_address="127.0.0.1"):
        Log.objects.create(user=actor,
                           action=cls.UNBAN_PROFILE,
                           object_id=user_id,
                           content_type=cls.USER,
                           text=text,
                           ip_address=ip_address)

    @classmethod
    def post_pending(cls, post, actor, ip_address="127.0.0.1"):
        Log.objects.create(user=actor,
                           action=2,
                           object_id=post.id,
                           content_type=1,
                           owner=post.user.id,
                           post_image=post.get_image_236()["url"],
                           ip_address=ip_address,
                           )

    @classmethod
    def update_profile(cls, actor, user_id,
                       text="", ip_address="127.0.0.1"):
        Log.objects.create(user=actor,
                           action=cls.UPDATE_PROFILE,
                           object_id=user_id,
                           content_type=cls.USER,
                           text=text,
                           # post_image=image,
                           ip_address=ip_address)


class ReportTypes(models.Model):
    title = models.CharField(max_length=250)
    pririty = models.IntegerField(default=0)


class ReportedPost(models.Model):
    post = models.OneToOneField(Post)
    cnt_report = models.IntegerField(default=0)
    priority = models.IntegerField(default=0)

    @classmethod
    def post_report(cls, post_id, reporter_id):
        reported, created = ReportedPost.objects.get_or_create(post_id=post_id)
        rpr, rpr_created = ReportedPostReporters.objects\
            .get_or_create(reported_post_id=reported.id, user_id=reporter_id)

        if rpr_created:
            ReportedPost.objects.filter(post_id=post_id)\
                .update(cnt_report=F('cnt_report') + 1)

            UserHistory.inc_user_stat(user_id=reporter_id,
                                      field="cnt_report")


class ReportedPostReporters(models.Model):
    reported_post = models.ForeignKey(ReportedPost)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    report_type = models.ForeignKey(ReportTypes, blank=True, default=None,
                                    null=True)
    create_time = models.DateTimeField(auto_now=True)


class UserHistory(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,
                                related_name="user_hiostory")
    pos_report = models.IntegerField(default=0)
    neg_report = models.IntegerField(default=0)
    cnt_report = models.IntegerField(default=0)
    admin_post_deleted = models.IntegerField(default=0)
    priority = models.IntegerField(default=1)

    @classmethod
    def inc_user_stat(cls, user_id, field, incr=1):
        user, created = UserHistory.objects.get_or_create(user_id=user_id)
        d = {
            field: F(field) + 1
        }
        UserHistory.objects.filter(user_id=user_id).update(**d)


class UserLog(models.Model):
    BAN_IMEI = 1
    DEBAN_IMEI = 2
    BAN_PROFILE = 3
    DEBAN_PROFILE = 4
    DEACTIVE = 5
    ACTIVE = 6
    ENABLE_POST = 7
    DISABLE_POST = 8
    ENABLE_REPORT = 9
    DISABLE_REPORT = 10
    ENABLE_COMMENT = 11
    DISABLE_COMMENT = 12

    ACTIONS = (
        (BAN_IMEI, _("BAN IMEI")),
        (DEBAN_IMEI, _("DEBAN IMEI")),
        (BAN_PROFILE, _("BAN PROFILE")),
        (DEBAN_PROFILE, _("DEBAN PROFILE")),
        (DEACTIVE, _("DEACTIVE")),
        (ACTIVE, _("ACTIVE")),
        (ENABLE_POST, _("ENABLE POST")),
        (DISABLE_POST, _("DISABLE POST")),
        (ENABLE_REPORT, _("ENABLE REPORT")),
        (DISABLE_REPORT, _("DISABLE REPORT")),
        (ENABLE_COMMENT, _("ENABLE COMMENT")),
        (DISABLE_COMMENT, _("DISABLE COMMENT")),
    )

    description = models.TextField()
    action = models.IntegerField(choices=ACTIONS, default=ACTIVE)
    create_time = models.DateTimeField(auto_now=True)

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_log")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name="actor_log")


class UserPermissions(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL)

    post = models.BooleanField(default=True)
    comment = models.BooleanField(default=True)
    report = models.BooleanField(default=True)


class UserCron(models.Model):
    ENABLE_POST = 1
    DISABLE_POST = 2
    ENABLE_REPORT = 3
    DISABLE_REPORT = 4
    ENABLE_COMMENT = 5
    DISABLE_COMMENT = 6

    ACTIONS = (
        (ENABLE_POST, _("ENABLE POST")),
        (DISABLE_POST, _("DISABLE POST")),
        (ENABLE_REPORT, _("ENABLE REPORT")),
        (DISABLE_REPORT, _("DISABLE REPORT")),
        (ENABLE_COMMENT, _("ENABLE COMMENT")),
        (DISABLE_COMMENT, _("DISABLE COMMENT")),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="user_cron")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name="actor_cron")

    due_date = models.DateTimeField(auto_now=True)
    action = models.IntegerField(choices=ACTIONS, default=ENABLE_POST)
    after = models.IntegerField(choices=ACTIONS, default=ENABLE_POST)
    create_time = models.DateTimeField()


class Commitment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    text_commitment = models.CharField(max_length=250)
    phone_data = models.ForeignKey(PhoneData)
    create_time = models.DateTimeField(auto_now=True)


class Results(models.Model):
    label = models.CharField(max_length=250)
    text = models.TextField()

    def get_label_text(self):
        return self.label.replace('_', ' ')

    def save(self, *args, **kwargs):
        self.label = self.label.replace(' ', '_')
        super(Results, self).save(*args, **kwargs)


class Official(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    mode = models.IntegerField(choices=((1, 'sp1'), (2, 'sp2')), default='1')


class Lable(models.Model):
    text = models.CharField(max_length=250)

    def __unicode__(self):
        return self.text


class UserActivitiesSample(models.Model):
    lable = models.ForeignKey(Lable, related_name='lable')
    categories = models.ManyToManyField(Category, through='UserLikeActivities')
    array = models.TextField(null=True, blank=True)
    # objects = models.Manager()


class UserLikeActivities(models.Model):
    score = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Category)
    user_activity = models.ForeignKey(UserActivitiesSample)


class UserActivities(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    activities = models.TextField()
    create_at = models.DateTimeField(null=True, blank=True)
    update_at = models.DateTimeField(null=True, blank=True)


class UserLable(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    lable = models.TextField(null=True, blank=True)


class Campaign(models.Model):
    title = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    primary_tag = models.CharField(blank=True, null=True, max_length=100)
    tags = models.TextField(null=True, blank=True)
    is_current = models.BooleanField(default=False)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    expired = models.BooleanField(default=False)
    winners = models.ManyToManyField(settings.AUTH_USER_MODEL,
                                     through="WinnersList")
    owner = models.ForeignKey(settings.AUTH_USER_MODEL,
                              related_name='campaign_owner')
    notif = models.BooleanField(default=True)
    logo = models.ImageField(default='', upload_to='pin/campaigns/')
    award = models.TextField(null=True, blank=True)
    help_text = models.TextField(null=True, blank=True)
    limit = models.IntegerField(default=0)


class WinnersList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.TextField(null=True, blank=True)
    rank = models.IntegerField(default=0)
    campaign = models.ForeignKey(Campaign)


class SystemState(models.Model):
    CACHE_NAME = 'system_state:writable'
    CACHE_TTL = 86400 * 30
    writable = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        super(SystemState, self).save(*args, **kwargs)
        cache.set(self.CACHE_NAME, self.writable, self.CACHE_TTL)


class FollowRequest(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_req')
    target = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='target')


class CampaignWinners(models.Model):
    COMPLETED = 2
    IN_PROGRESS = 1
    NOT_CALCULATE = 0

    STATUS_CHOICES = (
        (COMPLETED, _("completed")),
        (IN_PROGRESS, _("in progress")),
        (NOT_CALCULATE, _("not calculate")),
    )
    campaign = models.ForeignKey(Campaign)
    winners = models.TextField(null=True, blank=True)
    status = models.IntegerField(default=NOT_CALCULATE, blank=True,
                                 verbose_name=_("Status"),
                                 choices=STATUS_CHOICES)


class VerifyCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    code = models.IntegerField(unique=True)
    create_at = models.DateTimeField(auto_now_add=True)


class InviteLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    code = models.CharField(max_length=255, db_index=True)
    create_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def log(cls, user_id, code):
        cls.objects.create(user_id=user_id, code=code)


class RemoveImage(models.Model):
    PENDING = 0
    IN_PROGRESS = 1
    COMPLETED = 2

    STATUS_CHOICES = (
        (COMPLETED, _("completed")),
        (IN_PROGRESS, _("in progress")),
        (PENDING, _("pending")),
    )
    text = models.TextField()
    status = models.IntegerField(choices=STATUS_CHOICES, default=PENDING)

    @classmethod
    def remove_links(cls, sender, instance, created, *args, **kwargs):
        if created:
            links = instance.text.splitlines()
            servers = {
                'photos01': {'ip': '79.127.125.98',
                             'user': 'root',
                             'path': '/mnt/wisgoon/photos01/'},
                'photos02': {'ip': '79.127.125.99',
                             'user': 'root',
                             'path': '/mnt/wisgoon/photos02/'},
                'photos03': {'ip': '79.127.125.104',
                             'user': 'wisgoon',
                             'path': '/mnt/wisgoon/photos03/'},
                # 'moon': {'ip': '127.0.0.1',
                #          'user': 'amir',
                #          'path': '/home/amir/work/projects/wisgoon/feedreader/media/'}
            }

            # Create image list [{'timestamp': '1234567890', 'image_name':}]
            image_list = cls.get_image_list(links=links)

            # Change status
            instance.status = cls.IN_PROGRESS
            instance.save()
            link_list = []
            # Remove image from server and db
            for info in image_list:
                server_name = info["server_name"]
                image_path = info["image_path"]
                filename = info["image_name"]
                link = info["link"]
                folder_path = servers[server_name]["path"] + image_path
                link_list.append(link)
                try:
                    post = Post.objects.only('image')\
                        .get(timestamp=info["timestamp"])
                except:
                    print "Post not found. error: ", info
                    print "---------------------------------"
                    # Remove file from server
                    cls.delete_ssh(folder_path, filename,
                                   servers, server_name)
                    continue

                # Remove file from server
                cls.delete_ssh(folder_path, filename,
                               servers, server_name)

                # Remove post
                post_id = post.id
                post.delete()
                print "delete post {}".format(post_id)

            # Purge request for delete image linke
            cls.purge_request(link_list)
            print link_list

            # Change status
            instance.status = cls.COMPLETED
            instance.save()

    @classmethod
    def connect_to_server(cls, ip, username):
        import paramiko

        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip, username=username)
        except Exception, e:
            print str(e)
            time.sleep(3)
            cls.connect_to_server(ip, username)
        return ssh

    @classmethod
    def get_image_list(cls, links=[]):
        image_list = []
        for link in links:
            data = {}
            if len(link) > 0:
                slices = link.strip().split("/")

                if slices[-5] == 'avatars':

                    if slices[-1].startswith("64"):
                        timestamp = slices[-1][3:13]
                        image_name = slices[-1][3:]
                    else:
                        timestamp = slices[-1][0:10]
                        image_name = slices[-1]

                else:
                    if (slices[-1].startswith("500") or
                            slices[-1].startswith("236")):
                        timestamp = slices[-1][8:18]
                        image_name = slices[-1][8:]
                    else:
                        timestamp = slices[-1][0:10]
                        image_name = slices[-1]

                server_name = slices[2].split(".")[0]
                image_path = "/".join(slices[4:-1])

                data['image_name'] = image_name
                data['timestamp'] = int(timestamp)
                data['server_name'] = server_name
                data['image_path'] = image_path
                data['link'] = link
                image_list.append(data)
        return image_list

    @classmethod
    def delete_ssh(cls, folder_path, filename,
                   servers_info, server_name):
        ssh = cls.connect_to_server(
            ip=servers_info[server_name]["ip"],
            username=servers_info[server_name]["user"])

        # Create command an run
        cmd = "cd {} && rm *{}".format(folder_path, filename)
        try:
            ssh.exec_command(cmd)
            ssh.close()
        except Exception as e:
            print "error in run {}".format(cmd)
            print str(e)
            print "=================================="

    @classmethod
    def purge_request(cls, links=[]):
        import requests
        import json
        payload = {"files": links}
        headers = {'content-type': 'application/json',
                   'X-Auth-Email': 'vchakoshy@gmail.com',
                   'X-Auth-Key': '403fa50d139f603444f912ced5e2945064668'
                   }
        url = "https://api.cloudflare.com/client/v4/zones/06953b8ef5dce7efbac4e52797a9a908/purge_cache"
        res = requests.request("DELETE",
                               url,
                               data=json.dumps(payload),
                               headers=headers)
        print res.text

# class Acl(models.Model):
#         USER_SELF_TOPIC_STR = "/waw/topic/notif/user/{}/"

#         ALLOW_TYPE_DENY = 0
#         ALLOW_TYPE_ALLOW = 1

#         ALLOW_CHOICES = (
#             (ALLOW_TYPE_DENY, 'deny'),
#             (ALLOW_TYPE_ALLOW, 'allow'),
#         )

#         ACCESS_TYPE_SUBSCRIBE = 1
#         ACCESS_TYPE_PUBLISH = 2
#         ACCESS_TYPE_PUBSUB = 3

#         ACCESS_CHOICES = (
#             (ACCESS_TYPE_SUBSCRIBE, 'subscribe'),
#             (ACCESS_TYPE_PUBLISH, 'publish'),
#             (ACCESS_TYPE_PUBSUB, 'pubsub'),
#         )

#         allow = models.IntegerField(default=None, null=True, blank=True,
#                                     choices=ALLOW_CHOICES)
#         ipaddr = models.GenericIPAddressField(default=None,
#                                               null=True, blank=True)
#         username = models.CharField(default=None, null=True, blank=True,
#                                     max_length=100)
#         clientid = models.CharField(default=None, null=True, blank=True,
#                                     max_length=100)
#         access = models.IntegerField(choices=ACCESS_CHOICES)
#         topic = models.CharField(default="", max_length=200)
#         topic_crc = models.BigIntegerField(default=0, db_index=True)

#         @classmethod
#         def add_self_user_topics(cls, user_id, username):
#             from pin.tools import get_crc_32

#             topi = cls.USER_SELF_TOPIC_STR.format(user_id)
#             topi_crc = get_crc_32(topi)
#             cls.objects.get_or_create(topic=topi, topic_crc=topi_crc,
#                                       username=username,
#                                       access=cls.ACCESS_TYPE_PUBSUB,
#                                       allow=cls.ALLOW_TYPE_ALLOW)

#         def save(self, *args, **kwargs):
#             from pin.tools import get_crc_32

#             self.topic_crc = get_crc_32(self.topic)
#             if not self.ipaddr:
#                 self.ipaddr = None
#             if not self.clientid:
#                 self.clientid = None
#             if not self.username:
#                 self.username = None
#             super(Acl, self).save(*args, **kwargs)


post_save.connect(Stream.add_post, sender=Post)
post_save.connect(Likes.user_like_post, sender=Likes)
post_save.connect(Comments.add_comment, sender=Comments)
post_save.connect(Follow.new_follow, sender=Follow)
post_save.connect(RemoveImage.remove_links, sender=RemoveImage)
