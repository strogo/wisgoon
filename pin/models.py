# -*- coding: utf-8 -*-
import os
import time
import hashlib
import redis
#import datetime
from datetime import datetime, timedelta
from time import mktime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.core.validators import URLValidator
from django.db import models
from django.db.models import F
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from sorl.thumbnail import get_thumbnail

from taggit.managers import TaggableManager
from taggit.models import Tag

from model_mongo import Notif as Notif_mongo

LIKE_TO_DEFAULT_PAGE = 10

r_server = redis.Redis("localhost", db=11)

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
            'resource_uri': "/pin/apic/category/"+str(cat.id)+"/",
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
    url = models.CharField(blank=True, max_length=2000, validators=[URLValidator()])
    status = models.IntegerField(default=0, blank=True, verbose_name="وضعیت", choices=STATUS_CHOICES)
    device = models.IntegerField(default=1, blank=True)
    hash = models.CharField(max_length=32, blank=True, db_index=True)
    actions = models.IntegerField(default=1, blank=True)
    is_ads = models.BooleanField(default=False, blank=True, verbose_name="آگهی")
    view = models.IntegerField(default=0, db_index=True)
    show_in_default = models.BooleanField(default=False, blank=True,
        db_index=True, verbose_name='نمایش در خانه')

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

    def md5_for_file(self, f, block_size=2**20):
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

        super(Post, self).delete(*args, **kwargs)

    def date_lt(self, date, how_many_days=15):
        lt_date = datetime.now() - timedelta(days=how_many_days)
        lt_timestamp = mktime(lt_date.timetuple())
        timestamp = mktime(date.timetuple())
        #print timestamp, older_timestamp
        return timestamp < lt_timestamp

    @classmethod
    def hot(self, post_id, amount=1):
        r_server.zincrby('hot', int(post_id), amount=amount)
        r_server.zremrangebyrank('hot', 0, -1001)

    @classmethod
    def get_hot(self, values=False):
        h = r_server.zrange('hot', 0, 0, withscores=True, desc=True)
        if h[0][1] > 110:
            r_server.zincrby('hot', h[0][0], amount=-100)
        try:
            if values:
                post = Post.objects\
                    .values('id', 'text', 'cnt_comment', 'timestamp',
                            'image', 'user_id', 'cnt_like', 'category_id')\
                    .filter(id=h[0][0])
            else:
                post = Post.objects.filter(id=h[0][0])
            return post
        except Post.DoesNotExist:
            return False

    @classmethod
    def add_to_set(self, set_name, post, set_cat=True):
        r_server.zadd(set_name, int(post.timestamp), post.id)
        #r_server.ltrim(set_name, 0, 1000)
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
            profile.cnt_post += 1

            if ((self.date_lt( self.user.date_joined, 30) and profile.score > 5000) \
                or profile.score > 10000 ):
                profile.post_accept = True
                profile.save()
                self.status = 1

        except Profile.DoesNotExist:
            pass
     
        file_path = os.path.join(settings.MEDIA_ROOT, self.image)
        if os.path.exists(file_path):
            image_file = open(file_path)
           
            self.hash = self.md5_for_file(image_file)

        super(Post, self).save(*args, **kwargs)

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
            url = 'http://%s%s%s' % (Site.objects.get_current().domain, settings.MEDIA_URL, self.image)
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
        img = self.get_image_thumb()
        if img:
            return '<a href="/media/%s" target="_blank"><img src="%s" /></a>' % (self.image, img.url)
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

        Post.objects.filter(pk=self.id)\
            .update(status=self.APPROVED, timestamp=time.time())

        Post.add_to_set('post_latest', self)

        send_notif_bar(user=self.user.id, type=3, post=self.id, actor=self.user.id)


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='follower')
    following = models.ForeignKey(User, related_name='following')


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
            user = post.user
            followers = Follow.objects.all().filter(following=user)
            for follower in followers:
                try:
                    stream_set_key = "post_following_%s" % follower.follower_id
                    Post.add_to_set(stream_set_key, post, set_cat=False)

                    stream, created = Stream.objects\
                        .get_or_create(post=post,
                                       user=follower.follower,
                                       date=post.timestamp,
                                       following=user)
                except:
                    pass
        
        if post.status == Post.APPROVED:
            Post.add_to_set('post_latest', post)
                
    
class Likes(models.Model):
    user = models.ForeignKey(User, related_name='pin_post_user_like')
    post = models.ForeignKey(Post, related_name="post_item")
    ip = models.IPAddressField(default='127.0.0.1')
    
    class Meta:
        unique_together = (("post", "user"),)

    def save(self, *args, **kwargs):
        if not self.pk:
            Post.objects.filter(pk=self.post.id).update(cnt_like=F('cnt_like')+1)
        super(Likes, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        Post.objects.filter(pk=self.post.id).update(cnt_like=F('cnt_like')-1)

        key_str = "wis_likers_%d" % self.post.id
        r_server.srem(key_str, int(self.user.id))

        super(Likes, self).delete(*args, **kwargs)

    @classmethod
    def user_like_post(cls, sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user

        key_str = "wis_likers_%d" % post.id
        r_server.sadd(key_str, int(like.user.id))

        hcpstr = "like_max_%d" % post.id
        cp = cache.get(hcpstr)
        if cp:
            hstr = "like_cache_%s%s" % (post.id, cp)
            cache.delete(hstr)
            print "delete ", hstr, hcpstr

        str_likers = "web_likes_%s" % post.id
        all_likers = "post_like_%s" % (post.id)
        cache.delete(str_likers)

        Post.hot(post.id, amount=0.5)
        
        from pin.tasks import send_notif, send_notif_bar

        send_notif_bar(user=post.user_id, type=1, post=post.id, actor=sender.id)

    @classmethod
    def user_in_likers(self, post_id, user_id):
        key_str = "wis_likers_%d" % post_id
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
        (LIKE,'like'),
        (COMMENT,'comment'),
        (APPROVE,'approve'),
        (FAULT,'fault'))

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
        (LIKE,'like'),
        (COMMENT,'comment'),
        (APPROVE,'approve'),
        (FAULT,'fault'))

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
            Post.objects.filter(pk=self.object_pk.id).update(cnt_comment=F('cnt_comment')+1)
        try:
            if ((self.date_lt( self.user.date_joined, 5) and self.user.profile.score > 500) \
                or self.user.profile.score > 500 ):
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
        from pin.tasks import send_notif, send_notif_bar
        if not created:
            return None
        comment = instance
        post = comment.object_pk

        Post.hot(post.id, amount=1)

        if comment.user != post.user:
            #notif = send_notif(user=post.user, type=2, post=post.id, actor=comment.user)
            notif = send_notif_bar(user=post.user_id, type=2, post=post.id, actor=comment.user_id)

        for notif in Notif_mongo.objects.filter(type=2, post=post.id):
            #print "notif actors:", notif.actors
            for act in notif.actors:
                #print "actor is:", act
                if act != comment.user_id:
                    #print "no equal"
                    send_notif_bar(user=act, type=2, post=post.id, actor=comment.user_id)
                

                

    def delete(self, *args, **kwargs):
        Post.objects.filter(pk=self.object_pk.id).update(cnt_comment=F('cnt_comment')-1)
        super(Comments, self).delete(*args, **kwargs)

    @models.permalink
    def get_absolute_url(self):
        return ('pin-item', [str(self.object_pk_id)])

    def admin_link(self):        
        return '<a href="%s" target="_blank">مشاهده</a>' % (self.get_absolute_url())

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


post_save.connect(Stream.add_post, sender=Post)
post_save.connect(Likes.user_like_post, sender=Likes)
#post_delete.connect(Likes.user_unlike_post, sender=Likes)
post_save.connect(Post.change_tag_slug, sender=Tag)
post_save.connect(Comments.add_comment, sender=Comments)
