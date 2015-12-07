# -*- coding: utf-8 -*-
import os
import re
import time
import hashlib
import redis
import PIL

from PIL import Image
from textblob.classifiers import NaiveBayesClassifier

from datetime import datetime, timedelta
from time import mktime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.validators import URLValidator
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from sorl.thumbnail import get_thumbnail

from taggit.models import Tag

from model_mongo import Notif as Notif_mongo, MonthlyStats
from preprocessing import normalize_tags
from pin.tasks import delete_image
from pin.classification_tools import normalize

LIKE_TO_DEFAULT_PAGE = 10

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)
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

    def __unicode__(self):
        return self.title

    def admin_image(self):
        return '<img src="/media/%s" />' % self.image

    admin_image.allow_tags = True


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

    user = models.ForeignKey(User)
    owner = models.ForeignKey(User, related_name='owner',
                              blank=True, null=True)
    ended = models.BooleanField(default=False, db_index=True)
    cnt_view = models.IntegerField(default=0)
    post = models.ForeignKey("Post")
    ads_type = models.IntegerField(default=TYPE_1000_USER)
    start = models.DateTimeField(auto_now_add=True, auto_now=True)
    end = models.DateTimeField(blank=True, null=True)
    ip_address = models.IPAddressField(default="127.0.0.1")

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
                except Exception, e:
                    print str(e), "get add"

            return ad

        return None

    def save(self, *args, **kwargs):
        cache.delete("no_ad")
        self.owner = self.post.user
        super(Ad, self).save(*args, **kwargs)


class Category(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(default='', upload_to='pin/category/')
    parent = models.ForeignKey(SubCategory, related_name='sub_category',
                               blank=True, null=True)

    def __unicode__(self):
        return self.title

    def admin_image(self):
        return '<img src="/media/%s" />' % self.image

    admin_image.allow_tags = True

    @classmethod
    def get_json(cls, cat_id):
        # json cat cache str
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
        (PENDING, 'منتظر تایید'),
        (APPROVED, 'تایید شده'),
        (FAULT, 'تخلف'),
    )

    # title = models.CharField(max_length=250, blank=True)
    text = models.TextField(blank=True, verbose_name=_('Text'))
    image = models.CharField(max_length=500, verbose_name='تصویر')
    create_date = models.DateField(auto_now_add=True)
    create = models.DateTimeField(auto_now_add=True)
    timestamp = models.IntegerField(db_index=True, default=1347546432)
    user = models.ForeignKey(User)
    like = models.IntegerField(default=0)
    url = models.CharField(blank=True, max_length=2000,
                           validators=[URLValidator()])
    status = models.IntegerField(default=PENDING, blank=True,
                                 verbose_name="وضعیت",
                                 choices=STATUS_CHOICES)
    device = models.IntegerField(default=1, blank=True)
    hash = models.CharField(max_length=32, blank=True, db_index=True)
    actions = models.IntegerField(default=1, blank=True)
    is_ads = models.BooleanField(default=False, blank=True,
                                 verbose_name="آگهی")
    view = models.IntegerField(default=0, db_index=True)
    show_in_default = models.BooleanField(default=False, blank=True,
                                          db_index=True,
                                          verbose_name='نمایش در خانه')

    report = models.IntegerField(default=0, db_index=True)
    cnt_comment = models.IntegerField(default=0, blank=True)
    cnt_like = models.IntegerField(default=0, blank=True)
    # tags = TaggableManager(blank=True)

    height = models.IntegerField(default=-1, blank=True)
    width = models.IntegerField(default=-1, blank=True)

    category = models.ForeignKey(Category, default=1, verbose_name='گروه')
    objects = models.Manager()
    # accepted = AcceptedManager()

    data_236 = None
    data_500 = None

    def __unicode__(self):
        return self.text

    def get_pages(self):
        o = []
        text = self.text
        for r in Results.objects.all():
            # print r.id
            # print "check", r.get_label_text(), text
            # b = r.get_label_text() in text
            # print b
            if r.get_label_text() in text:
                new_url = reverse('pin-result', args=[r.label])
                href = '<a href="%s">%s</a>' % (new_url, r.get_label_text())
                o.append(href)
            # text = text.replace(r.get_label_text(), href)
        # print text
        return o

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

        ipath = "%s/%s" % (settings.MEDIA_ROOT, self.image)
        img = Image.open(ipath)
        Post.objects.filter(id=self.id)\
            .update(height=img.size[1], width=img.size[0])
        # self.height = img.size[1]
        # self.width = img.size[0]
        # self.save()
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
                    # print "get_image_236"
                    return False
                except Exception:
                    # print str(e), "get_image_236"
                    return False
                new_image_url = ibase + "/" + nname
                try:
                    p, created = PostMetaData.objects\
                        .get_or_create(post_id=self.id)

                    if not p.img_236_h:
                        p.img_236 = new_image_url
                        p.img_236_h = h
                        p.save()
                except Exception, e:
                    print str(e)

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
                    # print str(e), "get_image_500"
                    return False
                except Exception:
                    # print str(e), "get_image_500"
                    return False

                new_image_url = ibase + "/" + nname
                try:
                    p, created = PostMetaData.objects\
                        .get_or_create(post_id=self.id)
                    if not p.img_500_h:
                        p.img_500 = new_image_url
                        p.img_500_h = h
                        p.save()
                except Exception, e:
                    print str(e)

            except Exception:
                pass
                # print str(e)

        if api:
            final_url = new_image_url
        else:
            final_url = settings.MEDIA_PREFIX + "/media/" + new_image_url
        data = {
            'url': final_url,
            'h': int(h),
            'hw': "%dx%d" % (int(h), 500)
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
        try:
            file_path = os.path.join(settings.MEDIA_ROOT, self.image)
            delete_image.delay(file_path)
        except Exception, e:
            print str(e)

        r_server.srem('pending_photos', self.id)
        r_server.srem(settings.PENDINGS, int(self.id))
        r_server.lrem(settings.STREAM_LATEST, str(self.id))

        cat_stream = "%s_%s" % (settings.STREAM_LATEST, self.category.id)
        r_server.lrem(cat_stream, str(self.id))

        from user_profile.models import Profile
        n_score = 10 * self.cnt_like
        Profile.objects.filter(user_id=self.user_id)\
            .update(cnt_post=F('cnt_post') - 1, score=F('score') - n_score)

        from models_redis import LikesRedis
        LikesRedis(post_id=self.id).delete_likes()

        # from tasks import send_notif_bar

        # send_notif_bar(user=self.user.id, type=4, post=self.id,
        #                actor=self.user.id)

        super(Post, self).delete(*args, **kwargs)

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

        # print "this is add to stream"
        if not post.accept_for_stream():
            print "post not accepted for streams"
            return
        latest_stream = settings.STREAM_LATEST
        r_server.lrem(latest_stream, post.id)
        r_server.lpush(latest_stream, post.id)

        cat_stream = "%s_%s" % (settings.STREAM_LATEST_CAT, post.category.id)
        r_server.lrem(cat_stream, post.id)
        r_server.lpush(cat_stream, post.id)

        r_server.ltrim(cat_stream, 0, settings.LIST_LONG)
        r_server.ltrim(latest_stream, 0, settings.LIST_LONG)

    @classmethod
    def set_stream_to_redis(cls, user_id):
        user_stream = "%s_%d" % (settings.USER_STREAM, int(user_id))
        s = Stream.objects.filter(user_id=user_id)\
            .values_list('post_id', flat=True).order_by('-id')[:1000]
        for ss in s:
            r_server.rpush(user_stream, ss)

    @classmethod
    def add_to_user_stream(cls, post_id, user_id):
        user_stream = "%s_%d" % (settings.USER_STREAM, int(user_id))

        r_server.lrem(user_stream, post_id)
        r_server.lpush(user_stream, post_id)
        r_server.ltrim(user_stream, 0, 1000)

    @classmethod
    def add_to_set(cls, set_name, post, set_cat=True):
        r_server.zadd(set_name, int(post.timestamp), post.id)
        r_server.zremrangebyrank(set_name, 0, -1001)

        if set_cat:
            cat_set_key = "post_latest_%s" % post.category.id
            r_server.zadd(cat_set_key, int(post.timestamp), post.id)
            r_server.zremrangebyrank(cat_set_key, 0, -1001)
            # r_server.ltrim(cat_set_key, 0, 1000)

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
                # print "size:", img.size
                if img.size[0] < 236:
                    return False
            except Exception, e:
                print str(e), "models accept for stream"

        return True

    def save(self, *args, **kwargs):
        from user_profile.models import Profile
        try:
            profile = Profile.objects.get(user=self.user)

            if profile.score > settings.SCORE_FOR_STREAMS:
                self.status = 1

            else:
                print self.date_lt(self.user.date_joined, 30), profile.score
                # print "cant upload"

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
                # is_official = True

        else:
            print "path does not exists", file_path

        # print "self status: ", self.status

        self.text = normalize_tags(self.text)
        # print "all save"
        super(Post, self).save(*args, **kwargs)
        # print "after save - thumbnail "

    @models.permalink
    def get_absolute_url(self):
        return ('pin-item', [str(self.id)])

    def get_web_absolute_url(self):
        from pin.api_tools import abs_url

        return abs_url(reverse("pin-item",
                               kwargs={"item_id": self.id}),
                       api=False)

    def get_user_url(self):
        url = '/pin/user/%s' % (str(self.user_id))
        return '<a href="%s" target="_blank">%s</a>' % (url, self.user)
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

        # try:
        #     profile = Profile.objects.get(user=self.user)
        #     profile.save()
        # except Exception, e:
        #     print str(e), "views_device 71"

        send_notif_bar(user=self.user.id, type=3, post=self.id,
                       actor=self.user.id)

    @classmethod
    def home_latest(cls, pid=0):
        home_stream = settings.HOME_STREAM

        if not r_server.exists(home_stream):
            hposts = Post.objects.values_list('id', flat=True)\
                .filter(show_in_default=1).order_by('-timestamp')[:5000]
            if hposts:
                r_server.rpush(home_stream, *hposts)

        pl = r_server.lrange(home_stream, 0, settings.LIST_LONG)

        if pid == 0:
            return pl[:20]

        if pid:
            try:
                pid_index = pl.index(str(pid))
                idis = pl[pid_index + 1: pid_index + 20]
                return idis
            except ValueError:
                return []

        return []

    @classmethod
    def latest(cls, pid=0, cat_id=0):
        if cat_id:
            cat_stream = "%s_%s" % (settings.STREAM_LATEST_CAT, cat_id)
        else:
            cat_stream = settings.STREAM_LATEST

        if pid == 0:
            pl = r_server.lrange(cat_stream, 0, 20)
            print "1"
        else:
            print "12"

            cache_name = "cl_%s_%s" % (cat_stream, pid)
            cache_data = cache.get(cache_name)
            if cache_data:
                # print "we have cached data", cache_data, cache_name
                return cache_data
            pl = r_server.lrange(cat_stream, 0, -1)

        # print pl
        if pid == 0:
            return pl[:20]

        if pid:
            try:
                pid_index = pl.index(str(pid))
                idis = pl[pid_index + 1: pid_index + 20]
                cache.set(cache_name, idis, 86400)
                return idis
            except ValueError:
                return []

        return []

    @classmethod
    def last_likes(cls):
        pl = r_server.lrange(settings.LAST_LIKES, 0, 30)
        return pl[:30]

    @classmethod
    def user_stream_latest(cls, user_id, pid=0):
        row_per_page = 20
        # user_stream = "ustream_%d" % (user_id)
        if not user_id:
            return []
        user_stream = "%s_%d" % (settings.USER_STREAM, int(user_id))
        pl = r_server.lrange(user_stream, 0, 1000)
        if not pl:
            Post.set_stream_to_redis(user_id=user_id)
            pl = r_server.lrange(user_stream, 0, 1000)

        # print pl

        if pid == 0:
            import collections
            dups = [x for x, y in collections.Counter(pl).items() if y > 1]

            for dup in dups:
                r_server.lrem(user_stream, dup)

            return pl[:row_per_page]

        if pid:
            try:
                pid_index = pl.index(str(pid))
                idis = pl[pid_index + 1: pid_index + row_per_page]
                return idis
            except:
                return []

        return []


class Bills2(models.Model):
    COMPLETED = 1
    UNCOMPLETED = 0
    FAKERY = 2
    VALIDATE_ERROR = 3
    NOT_VALID = 4

    STATUS_CHOICES = (
        (COMPLETED, 'Completed'),
        (UNCOMPLETED, 'Uncompleted'),
        (FAKERY, 'Fakery'),
        (VALIDATE_ERROR, 'validate error'),
        (NOT_VALID, 'not valid'),
    )

    status = models.IntegerField(blank=True, null=True, default=0,
                                 choices=STATUS_CHOICES)
    amount = models.IntegerField(blank=True, null=True)
    trans_id = models.CharField(max_length=250, blank=True,
                                null=True, db_index=True)

    create_date = models.DateField(auto_now_add=True, default=datetime.now)
    create_time = models.DateTimeField(auto_now_add=True, default=datetime.now)

    user = models.ForeignKey(User)

    # def __init__(self):
    #     if Bills2.objects.all().count() == 0:
    #         from model_mongo import Bills
    #         for bb in Bills.objects.all():
    #             b = Bills2()
    #             b.status = bb.status
    #             b.amount = bb.amount
    #             b.trans_id = bb.trans_id
    #             b.user_id = bb.user
    #             b.save()


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='follower')
    following = models.ForeignKey(User, related_name='following')

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

        super(Follow, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        super(Follow, self).save(*args, **kwargs)

    @classmethod
    def new_follow(cls, sender, instance, *args, **kwargs):
        if kwargs['created']:
            from user_profile.models import Profile
            follower_id = instance.follower.id
            following_id = instance.following.id
            Profile.objects.filter(user_id=follower_id)\
                .update(cnt_following=F('cnt_following') + 1)

            Profile.objects.filter(user_id=following_id)\
                .update(cnt_followers=F('cnt_followers') + 1)

            # print "new follow"
            # print cls, sender, instance, args, kwargs
            # print "instance follow:", instance.follower.id
            Notif_mongo.objects.create(owner=instance.following.id, type=10,
                                       last_actor=instance.follower.id,
                                       date=datetime.now,
                                       seen=False)


class Stream(models.Model):
    following = models.ForeignKey(User, related_name='stream_following')
    user = models.ForeignKey(User, related_name='user')
    post = models.ForeignKey(Post)
    date = models.IntegerField(default=0)

    class Meta:
        unique_together = (("following", "user", "post"),)

    @classmethod
    def add_post(cls, sender, instance, *args, **kwargs):
        # print "here is add post in stream"
        post = instance
        post.get_image_236()
        post.get_image_500()
        post.get_image_sizes()
        if kwargs['created']:
            from pin.tasks import add_to_storage
            add_to_storage.delay(post_id=post.id)

            MonthlyStats.log_hit(object_type="post")

            from user_profile.models import Profile
            Profile.objects.filter(user_id=post.user_id)\
                .update(cnt_post=F('cnt_post') + 1)

            user = post.user

            Post.add_to_user_stream(post_id=post.id, user_id=user.id)

            from pin.actions import send_post_to_followers

            send_post_to_followers(user_id=user.id, post_id=post.id)

            if post.status == Post.APPROVED and post.accept_for_stream():
                Post.add_to_stream(post=post)


class Likes(models.Model):
    user = models.ForeignKey(User, related_name='pin_post_user_like')
    post = models.ForeignKey(Post, related_name="post_item")
    ip = models.IPAddressField(default='127.0.0.1')

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
        sender = like.user

        Post.objects.filter(pk=post.id).update(cnt_like=F('cnt_like') + 1)

        # Stroe last likes
        r_server.lrem(settings.LAST_LIKES, post.id)
        r_server.lpush(settings.LAST_LIKES, post.id)
        r_server.ltrim(settings.LAST_LIKES, 0, 1000)

        # Store user_last_likes
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
            print "delete ", hstr, hcpstr

        str_likers = "web_likes_%s" % post.id
        cache.delete(str_likers)

        # Post.hot(post.id, amount=0.5)
        from pin.actions import send_notif_bar

        send_notif_bar(user=post.user_id, type=1, post=post.id,
                       actor=sender.id)

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
        # print "come on"
        from models_redis import LikesRedis
        return LikesRedis(post_id=post_id).user_liked(user_id=user_id)

        key_str = "%s_%d" % (settings.POST_LIKERS, post_id)

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
        (LIKE, 'like'),
        (COMMENT, 'comment'),
        (APPROVE, 'approve'),
        (FAULT, 'fault')
    )

    post = models.ForeignKey(Post)
    actor = models.ForeignKey(User, related_name="actor_id")
    user = models.ForeignKey(User, related_name="post_user_id")
    seen = models.BooleanField(default=False)
    type = models.IntegerField(default=1, choices=TYPES)
    date = models.DateTimeField(auto_now_add=True)


class Notif(models.Model):
    LIKE = 1
    COMMENT = 2
    APPROVE = 3
    FAULT = 4
    TYPES = (
        (LIKE, 'like'),
        (COMMENT, 'comment'),
        (APPROVE, 'approve'),
        (FAULT, 'fault')
    )

    post = models.ForeignKey(Post)
    # sender = models.ForeignKey(User, related_name="sender")
    user = models.ForeignKey(User, related_name="user_id")
    text = models.CharField(max_length=500)
    seen = models.BooleanField(default=False)
    type = models.IntegerField(default=1, choices=TYPES)
    date = models.DateTimeField(auto_now_add=True)


class Notif_actors(models.Model):
    notif = models.ForeignKey(Notif, related_name="notif")
    actor = models.ForeignKey(User, related_name="actor")


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
    ip_address = models.IPAddressField(default='127.0.0.1', db_index=True)
    is_public = models.BooleanField(default=False, db_index=True)
    reported = models.BooleanField(default=False, db_index=True)

    object_pk = models.ForeignKey(Post, related_name='comment_post')
    user = models.ForeignKey(User, related_name='comment_sender')
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
        # print timestamp, older_timestamp
        return timestamp < lt_timestamp

    def save(self, *args, **kwargs):
        # from tools import check_spam
        from pin.classification import get_comment_category
        com_cat = str(get_comment_category(self.comment))
        if int(com_cat) in [2]:
            Log.bad_comment(post=self.object_pk,
                            actor=self.user,
                            ip_address=self.ip_address,
                            text=com_cat + " --- " + self.comment)
            return

        if (self.user.profile.score < settings.SCORE_FOR_COMMENING):
            return

        if not self.pk:
            Post.objects.filter(pk=self.object_pk_id)\
                .update(cnt_comment=F('cnt_comment') + 1)

        comment_cache_name = "com_%d" % int(self.object_pk_id)
        cache.delete(comment_cache_name)

        super(Comments, self).save(*args, **kwargs)

    @classmethod
    def add_comment(cls, sender, instance, created, *args, **kwargs):
        from pin.actions import send_notif_bar
        from pin.tools import get_post_user_cache
        if not created:
            return None

        MonthlyStats.log_hit(object_type=MonthlyStats.COMMENT)
        comment = instance
        post = get_post_user_cache(post_id=comment.object_pk_id)

        actors_list = []

        if comment.user_id != post.user_id:
            # if post.user_id == 1:
            #     import requests
            #     import json
            #     from daddy_avatar.templatetags.daddy_avatar import get_avatar
            #     pd = PhoneData.objects.only('google_token')\
            #         .get(user_id=post.user_id)

            #     data = {
            #         "to": pd.google_token,
            #         "data": {
            #             "message": {
            #                 "id": int("2%s" % comment.object_pk_id),
            #                 "avatar_url": "http://wisgoon.com%s" % get_avatar(comment.user_id, size=100),
            #                 "ticker": u"نظر جدید",
            #                 "title": u"نظر داده است",
            #                 "content": comment.comment,
            #                 "last_actor_name": comment.user.username,
            #                 "url": "wisgoon://wisgoon.com/pin/%s" % comment.object_pk_id,
            #                 "is_ad": False
            #             }
            #         }
            #     }

            #     res = requests.post(url='https://android.googleapis.com/gcm/send',
            #                         data=json.dumps(data),
            #                         headers={'Content-Type': 'application/json',
            #                                  'Authorization': 'key=AIzaSyAZ28bCEeqRa216NDPDRjHfF2IPC7fwkd4'})

            send_notif_bar(user=post.user_id, type=2, post=post.id,
                           actor=comment.user_id)

            actors_list.append(post.user_id)

        users = Comments.objects.filter(object_pk=post.id).values_list('user_id', flat=True)
        # for notif in Notif_mongo.objects.filter(type=2, post=post.id):
        for act in users:
            if act in actors_list:
                continue
            actors_list.append(act)
            if act != comment.user_id:
                send_notif_bar(user=act, type=2, post=post.id,
                               actor=comment.user_id)

    def delete(self, *args, **kwargs):
        Post.objects.filter(pk=self.object_pk.id)\
            .update(cnt_comment=F('cnt_comment') - 1)

        # print "here is delete comment"
        comment_cache_name = "com_%d" % self.object_pk.id
        cache.delete(comment_cache_name)
        super(Comments, self).delete(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('pin-item', [str(self.object_pk_id)])

    def admin_link(self):
        u = self.get_absolute_url()
        return '<a href="%s" target="_blank">مشاهده</a>' % (u)

    admin_link.allow_tags = True


class Comments_score(models.Model):
    comment = models.ForeignKey(Comments)
    user = models.ForeignKey(User, related_name='comment_like_user')
    score = models.IntegerField(default=0, blank=True)


class Report(models.Model):
    user = models.ForeignKey(User, related_name='report_user')
    post = models.ForeignKey(Post, related_name='report_post')

    class Meta:
        unique_together = (("post", "user"),)


class Block(models.Model):
    user = models.ForeignKey(User, related_name='blocker')
    blocked = models.ForeignKey(User, related_name='blocked')

    @classmethod
    def block_user(cls, user_id, blocked_id):
        if user_id == blocked_id:
            return False

        try:
            Block.objects.get_or_create(user_id=user_id, blocked_id=blocked_id)
        except:
            pass

        return True

    @classmethod
    def unblock_user(cls, user_id, blocked_id):
        if user_id == blocked_id:
            return False
        Block.objects.filter(user_id=user_id, blocked_id=blocked_id).delete()


class PhoneData(models.Model):
    user = models.OneToOneField(User, related_name="phone",
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
    # phone_brand = models.CharField(max_length=500)

    def get_need_fields(self):
        fields = self._meta.get_all_field_names()
        fields.remove(u'id')
        fields.remove('hash_data')
        fields.remove('logged_out')
        return fields

    def get_hash_data(self):
        h_str = ""
        fields = self.get_need_fields()

        h_str = '%'.join([str(getattr(self, f)) for f in fields])

        self.hash_data = hashlib.md5(h_str).hexdigest()
        return self.hash_data

    def save(self, *args, **kwargs):
        self.get_hash_data()
        super(PhoneData, self).save(*args, **kwargs)


class InstaAccount(models.Model):
    insta_id = models.IntegerField()
    cat = models.ForeignKey(Category)
    user = models.ForeignKey(User)
    lc = models.DateTimeField(auto_now_add=True, default=datetime.now())


class PostMetaData(models.Model):
    CREATED = 1
    FULL_IMAGE_CREATE = 2
    ERROR_IN_ORIGINAL = 3
    REDIS_CHANGE_SERVER = 4

    STATUS = (
        (CREATED, 'created'),
        (FULL_IMAGE_CREATE, 'full image create'),
        (ERROR_IN_ORIGINAL, 'error in original image'),
        (REDIS_CHANGE_SERVER, 'redis server change'),
    )

    post = models.OneToOneField(Post)
    original_size = models.IntegerField(default=0)
    status = models.IntegerField(default=CREATED, choices=STATUS, db_index=True)
    img_236_h = models.IntegerField(default=0)
    img_500_h = models.IntegerField(default=0)
    img_236 = models.CharField(max_length=250)
    img_500 = models.CharField(max_length=250)


class BannedImei(models.Model):
    imei = models.CharField(max_length=50, db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, auto_now=True, default=datetime.now())


class Log(models.Model):
    POST = 1
    COMMENT = 2
    USER = 3
    COMMENT_TEST = 4

    TYPES = (
        (POST, "post"),
        (COMMENT, "comment"),
        (USER, "user"),
        (COMMENT_TEST, 'comment test'),
    )

    DELETE = 1
    PENDING = 2
    BAD_COMMENT = 3
    BAD_POST = 4
    BAN_IMEI = 5
    BAN_ADMIN = 6
    ACTIONS = (
        (DELETE, "delete"),
        (PENDING, "pending"),
        (BAD_COMMENT, "bad comment"),
        (BAD_POST, "bad post"),
        (BAN_IMEI, "ban imei"),
        (BAN_ADMIN, "ban by admin"),
    )

    user = models.ForeignKey(User)
    action = models.IntegerField(default=1, choices=ACTIONS, db_index=True)
    object_id = models.IntegerField(default=0, db_index=True)
    content_type = models.IntegerField(default=1, choices=TYPES, db_index=True)
    ip_address = models.IPAddressField(default='127.0.0.1', db_index=True)
    owner = models.IntegerField(default=0)
    text = models.TextField(default="", blank=True, null=True)

    create_time = models.DateTimeField(auto_now_add=True, auto_now=True, default=datetime.now())

    post_image = models.CharField(max_length=250, blank=True, null=True)

    @classmethod
    def post_delete(cls, post, actor, ip_address="127.0.0.1"):
        try:
            img_url = post.get_image_236()["url"]
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
        Log.objects.create(user_id=actor.id,
                           action=Log.BAN_ADMIN,
                           content_type=Log.USER,
                           object_id=user_id,
                           text=text,
                           ip_address=ip_address)

    @classmethod
    def ban_by_imei(cls, actor, text="", ip_address="127.0.0.1"):
        Log.objects.create(user_id=actor.id,
                           action=5,
                           content_type=3,
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


class Results(models.Model):
    label = models.CharField(max_length=250)
    text = models.TextField()

    def get_label_text(self):
        return self.label.replace('_', ' ')

    def save(self, *args, **kwargs):
        self.label = self.label.replace(' ', '_')
        super(Results, self).save(*args, **kwargs)


class Official(models.Model):
    user = models.ForeignKey(User)
    mode = models.IntegerField(choices=((1, 'sp1'), (2, 'sp2')), default='1')

post_save.connect(Stream.add_post, sender=Post)
post_save.connect(Likes.user_like_post, sender=Likes)
# post_delete.connect(Likes.user_unlike_post, sender=Likes)
post_save.connect(Post.change_tag_slug, sender=Tag)
post_save.connect(Comments.add_comment, sender=Comments)
post_save.connect(Follow.new_follow, sender=Follow)
# post_delete.connect(Follow.un_follow, sender=Follow)
