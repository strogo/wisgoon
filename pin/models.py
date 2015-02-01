# -*- coding: utf-8 -*-
import os
import re
import time
import hashlib
import redis
import PIL

from PIL import Image

#import datetime
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

from taggit.managers import TaggableManager
from taggit.models import Tag

from model_mongo import Notif as Notif_mongo, MonthlyStats, PostMeta, PendingPosts

LIKE_TO_DEFAULT_PAGE = 10

r_server = redis.Redis(settings.REDIS_DB, db=settings.REDIS_DB_NUMBER)


class Category(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(default='', upload_to='pin/category/')

    def __unicode__(self):
        return self.title

    def admin_image(self):
        return '<img src="/media/%s" />' % self.image

    admin_image.allow_tags = True

    @classmethod
    def get_json(self, cat_id):
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


class AcceptedManager(models.Manager):
    def get_query_set(self):
        return super(AcceptedManager, self).get_query_set().filter(status=1)


class Post(models.Model):
    PENDING = 0
    APPROVED = 1
    FAULT = 2

    META_DATA = None

    NEED_KEYS = ['id', 'text', 'cnt_comment', 'timestamp',
                 'image', 'user_id', 'cnt_like', 'category_id',
                 'status', 'url']

    NEED_KEYS2 = ['id', 'text', 'cnt_comment', 'timestamp',
                  'image', 'user', 'cnt_like', 'category',
                  'status', 'url']

    NEED_KEYS_WEB = ['id', 'text', 'cnt_comment', 'cnt_like', 'user',
                     'show_in_default']

    STATUS_CHOICES = (
        (PENDING, 'منتظر تایید'),
        (APPROVED, 'تایید شده'),
        (FAULT, 'تخلف'),
    )

    #title = models.CharField(max_length=250, blank=True)
    text = models.TextField(blank=True, verbose_name=_('Text'))
    image = models.CharField(max_length=500, verbose_name='تصویر')
    create_date = models.DateField(auto_now_add=True)
    create = models.DateTimeField(auto_now_add=True)
    timestamp = models.IntegerField(db_index=True, default=1347546432)
    user = models.ForeignKey(User)
    like = models.IntegerField(default=0)
    url = models.CharField(blank=True, max_length=2000,
                           validators=[URLValidator()])
    status = models.IntegerField(default=0, blank=True, verbose_name="وضعیت",
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
    cnt_comment = models.IntegerField(default=-1, blank=True)
    cnt_like = models.IntegerField(default=0, blank=True)
    tags = TaggableManager(blank=True)

    height = models.IntegerField(default=-1, blank=True)
    width = models.IntegerField(default=-1, blank=True)

    category = models.ForeignKey(Category, default=1, verbose_name='گروه')
    objects = models.Manager()
    accepted = AcceptedManager()

    def __unicode__(self):
        return self.text

    def is_pending(self):
        if PendingPosts.objects(post=int(self.id)).count():
            return True

        return False

    def get_tags(self):
        hash_tags = re.compile(ur'(?i)(?<=\#)\w+', re.UNICODE)
        tags = hash_tags.findall(self.text)
        all_tags = []
        for t in tags:
            if t not in all_tags:
                all_tags.append(t)
        return all_tags

    def save_thumb(self, basewidth):
        ibase = os.path.dirname(self.image)
        ipath = "%s/%s" % (settings.MEDIA_ROOT, self.image)
        idir = os.path.dirname(ipath)
        iname = os.path.basename(ipath)
        
        img = Image.open(ipath)
        
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth, hsize), PIL.Image.ANTIALIAS)
        w, h = img.size
        nname = "%dx%d_%s" % (w, h, iname)
        npath = "%s/%s" % (idir, nname)
        img.save(npath)

        return ibase, nname, h

    def get_image_236(self, api=False):
        cname = "pmeta_%d_236" % int(self.id)
        ccache = cache.get(cname)
        if ccache:
            new_image_url, h = ccache.split(":")
        else:

            try:
                imeta = PostMeta.objects.get(post=int(self.id))
                if not imeta.img_236:
                    raise PostMeta.DoesNotExist
                new_image_url = imeta.img_236
                h = imeta.img_236_h
                
                a = [new_image_url, str(h)]
                d = ":".join(a)
                cache.set(cname, d, 86400)
            except PostMeta.DoesNotExist:
                try:
                    ibase, nname, h = self.save_thumb(basewidth=236)
                except IOError, e:
                    # print str(e), "get_image_236"
                    return False
                except Exception, e:
                    # print str(e), "get_image_236"
                    return False

                new_image_url = ibase + "/" + nname
                PostMeta.objects(post=self.id)\
                    .update(set__img_236=new_image_url,
                            set__img_236_h=h,
                            upsert=True)

        if api:
            final_url = new_image_url
        else:
            final_url = settings.MEDIA_PREFIX + "/media/" + new_image_url
        data = {
            'url': final_url,
            'h': int(h),
            'hw': "%dx%d" % (int(h), 236)
        }

        return data

    def get_image_500(self, api=False):
        cname = "pmeta_%d_500" % int(self.id)
        ccache = cache.get(cname)
        if ccache:
            new_image_url, h = ccache.split(":")
        else:

            try:
                imeta = PostMeta.objects.get(post=int(self.id))
                if not imeta.img_500:
                    raise PostMeta.DoesNotExist
                new_image_url = imeta.img_500
                h = imeta.img_500_h

                a = [new_image_url, str(h)]
                d = ":".join(a)
                cache.set(cname, d, 86400)

            except PostMeta.DoesNotExist:
                try:
                    ibase, nname, h = self.save_thumb(basewidth=500)
                except IOError, e:
                    print str(e), "get_image_500"
                    return False
                except Exception, e:
                    print str(e), "get_image_500"
                    return False

                new_image_url = ibase + "/" + nname
                PostMeta.objects(post=self.id)\
                    .update(set__img_500=new_image_url,
                            set__img_500_h=h,
                            upsert=True)

            except Exception, e:
                print str(e)

        if api:
            final_url = new_image_url
        else:
            final_url = settings.MEDIA_PREFIX + "/media/" + new_image_url
        data = {
            'url': final_url,
            'h': int(h),
            'hw': "%dx%d" % (int(h), 500)
        }

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
            os.remove(file_path)
        except Exception, e:
            print str(e)

        r_server.srem('pending_photos', self.id)
        r_server.srem(settings.PENDINGS, int(self.id))
        r_server.lrem(settings.STREAM_LATEST, str(self.id))

        cat_stream = "%s_%s" % (settings.STREAM_LATEST, self.category.id)
        r_server.lrem(cat_stream, str(self.id))

        from user_profile.models import Profile
        Profile.objects.filter(user_id=self.user_id)\
            .update(cnt_post=F('cnt_post') - 1)

        super(Post, self).delete(*args, **kwargs)

    def date_lt(self, date, how_many_days=15):
        lt_date = datetime.now() - timedelta(days=how_many_days)
        lt_timestamp = mktime(lt_date.timetuple())
        timestamp = mktime(date.timetuple())
        #print timestamp, older_timestamp
        return timestamp < lt_timestamp

    @classmethod
    def hot(self, post_id, amount=1):
        hotest = r_server.smembers('hottest')
        if str(post_id) not in hotest:
            r_server.zincrby('hot', int(post_id), amount=1)

        r_server.zremrangebyrank('hot', 0, -1001)

    @classmethod
    def get_hot(self, values=False):
        h = r_server.zrange('hot', 0, 0, withscores=True, desc=True)
        if h[0][1] > 110:
            r_server.sadd('hottest', h[0][0])
            r_server.zincrby('hot', h[0][0], amount=-100)

        if h[0][1] <= 49:
            return False

        if values:
            post = Post.objects\
                .values(*self.NEED_KEYS)\
                .filter(id=h[0][0])
        else:
            post = Post.objects.filter(id=h[0][0])

        if not post:
            r_server.zrem('hot', h[0][0])
        return post

    @classmethod
    def add_to_stream(self, post):
        latest_stream = settings.STREAM_LATEST
        r_server.lrem(latest_stream, post.id)
        r_server.lpush(latest_stream, post.id)

        cat_stream = "%s_%s" % (settings.STREAM_LATEST_CAT, post.category.id)
        r_server.lrem(cat_stream, post.id)
        r_server.lpush(cat_stream, post.id)

        r_server.ltrim(cat_stream, 0, settings.LIST_LONG)
        r_server.ltrim(latest_stream, 0, settings.LIST_LONG)

    @classmethod
    def set_stream_to_redis(self, user_id):
        user_stream = "%s_%d" % (settings.USER_STREAM, int(user_id))
        s = Stream.objects.filter(user_id=user_id)\
            .values_list('post_id', flat=True).order_by('-id')[:1000]
        for ss in s:
            r_server.rpush(user_stream, ss)

    @classmethod
    def add_to_user_stream(self, post, user_id):
        user_stream = "%s_%d" % (settings.USER_STREAM, int(user_id))

        pl = r_server.lrange(user_stream, 0, 1000)
        if not pl:
            Post.set_stream_to_redis(user_id=user_id)
            pl = r_server.lrange(user_stream, 0, 1000)

        if str(post.id) not in pl:
            r_server.lpush(user_stream, post.id)

        r_server.ltrim(user_stream, 0, 1000)

    @classmethod
    def add_to_set(self, set_name, post, set_cat=True):
        r_server.zadd(set_name, int(post.timestamp), post.id)
        r_server.zremrangebyrank(set_name, 0, -1001)

        if set_cat:
            cat_set_key = "post_latest_%s" % post.category.id
            r_server.zadd(cat_set_key, int(post.timestamp), post.id)
            r_server.zremrangebyrank(cat_set_key, 0, -1001)
            #r_server.ltrim(cat_set_key, 0, 1000)

    def save(self, *args, **kwargs):
        from user_profile.models import Profile
        try:
            profile = Profile.objects.get(user=self.user)

            if ((self.date_lt(self.user.date_joined, 30) and
                 profile.score > 5000) or profile.score > 7000):
                self.status = 1

        except Profile.DoesNotExist:
            pass

        file_path = os.path.join(settings.MEDIA_ROOT, self.image)
        if os.path.exists(file_path):
            image_file = open(file_path)

            self.hash = self.md5_for_file(image_file)

        super(Post, self).save(*args, **kwargs)
        self.get_image_236()

    @models.permalink
    def get_absolute_url(self):
        return ('pin-item', [str(self.id)])

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
        #return Likes.objects.filter(post_id=self.id).count()

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
        print "current approve:", self.status

        Post.objects.filter(pk=self.id)\
            .update(status=self.APPROVED, timestamp=time.time())

        #Post.add_to_set('post_latest', self)
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
    def home_latest(self, pid=0):
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
    def latest(self, pid=0, cat_id=0):
        # print "this is latest", pid, cat_id
        # print pid

        if cat_id:
            cat_stream = "%s_%s" % (settings.STREAM_LATEST_CAT, cat_id)
        else:
            cat_stream = settings.STREAM_LATEST

        if pid == 0:
            pl = r_server.lrange(cat_stream, 0, 20)
        else:
            cache_name = "cl_%s_%s" % (cat_stream, pid)
            cache_data = cache.get(cache_name)
            if cache_data:
                # print "we have cached data", cache_data, cache_name
                return cache_data
            pl = r_server.lrange(cat_stream, 0, settings.LIST_LONG)

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
    def last_likes(self):
        pl = r_server.lrange(settings.LAST_LIKES, 0, 30)
        return pl[:30]

    @classmethod
    def user_stream_latest(self, user_id, pid=0):
        ROW_IN_PAGE = 20
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

            return pl[:ROW_IN_PAGE]

        if pid:
            try:
                pid_index = pl.index(str(pid))
                idis = pl[pid_index + 1: pid_index + ROW_IN_PAGE]
                return idis
            except:
                return []

        return []


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='follower')
    following = models.ForeignKey(User, related_name='following')

    @classmethod
    def get_follow_status(self, follower, following):
        fstatus = Follow.objects.filter(follower_id=follower,
                                        following_id=following).exists()
        return fstatus

    @classmethod
    def new_follow(cls, sender, instance, *args, **kwargs):
        pass
        # print "new follow"
        # print cls, sender, instance, args, kwargs
        # print "instance follow:", instance.follower.id
        # Notif_mongo.objects(owner=instance.following.id, type=10, post=0)\
        #     .update_one(set__last_actor=instance.follower.id,
        #                 set__date=datetime.now,
        #                 set__seen=False,
        #                 add_to_set__actors=instance.follower.id, upsert=True)


class Stream(models.Model):
    following = models.ForeignKey(User, related_name='stream_following')
    user = models.ForeignKey(User, related_name='user')
    post = models.ForeignKey(Post)
    date = models.IntegerField(default=0)

    class Meta:
        unique_together = (("following", "user", "post"),)

    @classmethod
    def add_post(cls, sender, instance, *args, **kwargs):
        post = instance
        if kwargs['created']:

            MonthlyStats.log_hit(object_type="post")

            from user_profile.models import Profile
            Profile.objects.filter(user_id=post.user_id)\
                .update(cnt_post=F('cnt_post') + 1)

            user = post.user

            Post.add_to_user_stream(post=post, user_id=user.id)

            followers = Follow.objects.all().filter(following=user)
            for follower in followers:
                try:
                    Post.add_to_user_stream(post=post, user_id=follower.follower.id)
                except:
                    pass

            if post.status == Post.APPROVED:
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

        user_last_likes = "%s_%d" % (settings.USER_LAST_LIKES, int(self.user.id))
        r_server.lrem(user_last_likes, self.post.id)

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
        user_last_likes = "%s_%d" % (settings.USER_LAST_LIKES, int(like.user.id))
        if not r_server.exists(user_last_likes):
            likes = Likes.objects.values_list('post_id', flat=True)\
                .filter(user_id=like.user.id).order_by('-id')[:1000]
            r_server.rpush(user_last_likes, *likes)
        else:
            r_server.lrem(user_last_likes, post.id)
            r_server.lpush(user_last_likes, post.id)
            r_server.ltrim(user_last_likes, 0, 1000)

        Profile.after_like(user_id=post.user_id)

        key_str = "%s_%d" % (settings.POST_LIKERS, post.id)
        r_server.sadd(key_str, int(like.user.id))

        hcpstr = "like_max_%d" % post.id
        cp = cache.get(hcpstr)
        if cp:
            hstr = "like_cache_%s%s" % (post.id, cp)
            cache.delete(hstr)
            print "delete ", hstr, hcpstr

        str_likers = "web_likes_%s" % post.id
        cache.delete(str_likers)

        Post.hot(post.id, amount=0.5)
        from pin.tasks import send_notif_bar

        send_notif_bar(user=post.user_id, type=1, post=post.id,
                       actor=sender.id)

    @classmethod
    def user_likes(self, user_id, pid=0):
        ROW_IN_PAGE = 20

        user_last_likes = "%s_%d" % (settings.USER_LAST_LIKES, int(user_id))

        if not r_server.exists(user_last_likes):
            likes = Likes.objects.values_list('post_id', flat=True)\
                .filter(user_id=user_id).order_by('-id')[:1000]
            if likes:
                r_server.rpush(user_last_likes, *likes)
            else:
                r_server.rpush(user_last_likes, [])

        pl = r_server.lrange(user_last_likes, 0, 1000)
        if pid:
            try:
                pid_index = pl.index(str(pid))
            except ValueError:
                return []
            idis = pl[pid_index + 1: pid_index + ROW_IN_PAGE]
            return idis
        
        return pl[:20]

    @classmethod
    def user_in_likers(self, post_id, user_id):
        key_str = "%s_%d" % (settings.POST_LIKERS, post_id)
        post_likers = r_server.smembers(key_str)
        if post_likers == set([]):
            post_likers = Likes.objects.values_list('user_id', flat=True)\
                .filter(post_id=post_id)

            if post_likers:
                for pl in post_likers:
                    r_server.sadd(key_str, int(pl))
            else:
                r_server.sadd(key_str, int(-1))

        if str(user_id) in post_likers or user_id in post_likers:
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
    #sender = models.ForeignKey(User, related_name="sender")
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
    comment = models.TextField()
    submit_date = models.DateTimeField(auto_now_add=True)
    ip_address = models.IPAddressField(default='127.0.0.1', db_index=True)
    is_public = models.BooleanField(default=False, db_index=True)
    reported = models.BooleanField(default=False, db_index=True)

    object_pk = models.ForeignKey(Post, related_name='comment_post')
    user = models.ForeignKey(User, related_name='comment_sender')
    score = models.IntegerField(default=0, blank=True, )

    def date_lt(self, date, how_many_days=15):
        lt_date = datetime.now() - timedelta(days=how_many_days)
        lt_timestamp = mktime(lt_date.timetuple())
        timestamp = mktime(date.timetuple())
        #print timestamp, older_timestamp
        return timestamp < lt_timestamp

    def save(self, *args, **kwargs):
        if not self.pk:
            Post.objects.filter(pk=self.object_pk.id)\
                .update(cnt_comment=F('cnt_comment') + 1)
        try:
            ps = self.user.profile.score
            if ((self.date_lt(self.user.date_joined, 5) and
                 ps > 500) or ps > 500):
                self.is_public = True
        except:
            pass

        hcpstr = "cmnt_max_%d" % self.object_pk.id
        cp = cache.get(hcpstr)
        if cp:
            hstr = "cmn_cache_%s%s" % (self.object_pk.id, cp)
            cache.delete(hstr)
            print "delete ", hstr, hcpstr

        super(Comments, self).save(*args, **kwargs)

    @classmethod
    def add_comment(cls, sender, instance, created, *args, **kwargs):
        from pin.tasks import send_notif_bar
        if not created:
            return None

        MonthlyStats.log_hit(object_type=MonthlyStats.COMMENT)
        comment = instance
        post = comment.object_pk

        Post.hot(post.id, amount=1)

        if comment.user != post.user:
            notif = send_notif_bar(user=post.user_id, type=2, post=post.id,
                                   actor=comment.user_id)

        for notif in Notif_mongo.objects.filter(type=2, post=post.id):
            #print "notif actors:", notif.actors
            for act in notif.actors:
                #print "actor is:", act
                if act != comment.user_id:
                    #print "no equal"
                    send_notif_bar(user=act, type=2, post=post.id,
                                   actor=comment.user_id)

    def delete(self, *args, **kwargs):
        Post.objects.filter(pk=self.object_pk.id)\
            .update(cnt_comment=F('cnt_comment') - 1)
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
    def block_user(self, user_id, blocked_id):
        if user_id == blocked_id:
            return False

        try:
            Block.objects.get_or_create(user_id=user_id, blocked_id=blocked_id)
        except:
            pass

        return True

    @classmethod
    def unblock_user(self, user_id, blocked_id):
        if user_id == blocked_id:
            return False
        Block.objects.filter(user_id=user_id, blocked_id=blocked_id).delete()


post_save.connect(Stream.add_post, sender=Post)
post_save.connect(Likes.user_like_post, sender=Likes)
#post_delete.connect(Likes.user_unlike_post, sender=Likes)
post_save.connect(Post.change_tag_slug, sender=Tag)
post_save.connect(Comments.add_comment, sender=Comments)
post_save.connect(Follow.new_follow, sender=Follow)
