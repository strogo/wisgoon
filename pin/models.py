# -*- coding: utf-8 -*- 
import os
import hashlib
import datetime
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.comments.models import Comment
from django.contrib.comments.signals import comment_was_posted
from django.contrib.sites.models import Site
from django.core.validators import URLValidator
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.utils.translation import ugettext_lazy as _

from sorl.thumbnail import get_thumbnail

from taggit.managers import TaggableManager
from taggit.models import Tag


class Category(models.Model):
    title = models.CharField(max_length=250)
    image = models.ImageField(default='', upload_to='pin/category/')
    
    def __unicode__(self):
        return self.title
    
    def admin_image(self):
        return '<img src="/media/%s" />' % self.image

    admin_image.allow_tags = True

class Post(models.Model):
    #title = models.CharField(max_length=250, blank=True)
    text = models.TextField(blank=True, verbose_name=_('Text'))
    image = models.CharField(max_length=500, verbose_name='تصویر')
    create_date = models.DateField(auto_now_add=True)
    create = models.DateTimeField(auto_now_add=True)
    timestamp = models.IntegerField(db_index=True, default=1347546432)
    user = models.ForeignKey(User)
    like = models.IntegerField(default=0)
    url = models.CharField(blank=True, max_length=2000, validators=[URLValidator()])
    status = models.IntegerField(default=0, blank=True)
    device = models.IntegerField(default=1, blank=True)
    hash = models.CharField(max_length=32, blank=True, db_index=True)
    actions = models.IntegerField(default=1, blank=True)
    is_ads = models.BooleanField(default=False, blank=True)
    
    tags = TaggableManager(blank=True)

    category = models.ForeignKey(Category, default=1)
    
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
        except:
            pass

        super(Post, self).delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        from user_profile.models import Profile
        
        try:       
            #profile = Profile.objects.get(user=self.user)
            if self.user.profile.trusted :
                self.status=1
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
    
    def get_host_url(self):
        abs=self.get_absolute_url()
        
        if settings.DEBUG:
            return abs 
        else:
            host_url='http://%s%s' % (Site.objects.get_current().domain, abs)
            return host_url
    
    def get_image_absolute_url(self):
        if settings.DEBUG:
            url='%s%s' % (settings.MEDIA_URL, self.image)
        else:
            url='http://%s%s%s' % (Site.objects.get_current().domain, settings.MEDIA_URL, self.image)
        return url

    def get_image_thumb(self):
        try:
            im = get_thumbnail(self.image, '192', crop='center', quality=99)
        except:
            im = None
        return im

    @classmethod
    def change_tag_slug(cls, sender, instance, *args, **kwargs):
        if kwargs['created']:
            tag = instance
            tag.slug = '-'.join(tag.name.split())#And clean title, and make sure this is unique.
            tag.save()

    def admin_image(self):
        img = self.get_image_thumb()
        
        return '<a href="/media/%s" target="_blank"><img src="%s" /></a>' % (self.image, img.url)
    admin_image.allow_tags = True

class Follow(models.Model):
    follower = models.ForeignKey(User ,related_name='follower')
    following = models.ForeignKey(User, related_name='following')

class Stream(models.Model):
    following = models.ForeignKey(User, related_name='stream_following')
    user = models.ForeignKey(User ,related_name='user')
    post = models.ForeignKey(Post)
    date = models.IntegerField(default=0)
    
    class Meta:
        unique_together = (("following", "user", "post"),)

    @classmethod
    def add_post(cls, sender, instance, *args, **kwargs):
        post = instance
        user = post.user
        followers = Follow.objects.all().filter(following=user)
        for follower in followers:
            stream, created = Stream.objects.get_or_create(post=post, user=follower.follower, date=post.timestamp, following=user)
            
    
class Likes(models.Model):
    user = models.ForeignKey(User,related_name='pin_post_user_like')
    post = models.ForeignKey(Post, related_name="post_item")
    
    class Meta:
        unique_together = (("post", "user"),)
        
    @classmethod
    def user_like_post(cls, sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        
        notify, created = Notify.objects.get_or_create(post=post, user=post.user, type=1)
        notify.date = datetime.datetime.now()
        notify.actors.add(sender) 
        notify.save()
        #notify.post = post
        #notify.sender = sender
        #notify.user = post.user
        #notify.text = 'like this'
        #notify.save()
        
    
    @classmethod
    def user_unlike_post(cls, sender, instance, *args, **kwargs):
        like = instance
        post = like.post
        sender = like.user
        
        try:
            notify = Notify.objects.get(type=1,post=post)
            if notify.actors:
                notify.actors.remove(sender)
            else:
                notify.delete()

            if not notify.actors.all():
                notify.delete()
        except Notify.DoesNotExist:
            pass
        

class Notify(models.Model):
    TYPES = ((1,'like'),(2,'comment'))
    
    post = models.ForeignKey(Post)
    #sender = models.ForeignKey(User, related_name="sender")
    user = models.ForeignKey(User, related_name="userid")
    text = models.CharField(max_length=500)
    seen = models.BooleanField(default=False)
    type = models.IntegerField(default=1, choices=TYPES) # 1=Post_like, 2=Post_comment
    date = models.DateTimeField(auto_now_add=True)
    actors = models.ManyToManyField(User, related_name="actors")

class App_data(models.Model):
    name = models.CharField(max_length=250)
    file = models.FileField(upload_to='app')
    version = models.CharField(max_length=50)
    current = models.BooleanField(default=1)

def user_comment_post(sender, **kwargs):
    if 'pin.post' in kwargs['request'].POST['content_type']:
        comment = kwargs['comment']
        post_id = kwargs['request'].POST['object_pk']
        post = Post.objects.get(pk=post_id)
        if comment.user != post.user:
            #post = comment.post
            sender = comment.user
                
            notify, created = Notify.objects.get_or_create(post=post, user=post.user, type=2)
            #notify.post = post
            #notify.sender = sender
            #notify.user = post.user
            #notify.text = 'comment this'
            #notify.type = 2
            notify.date = datetime.datetime.now()
            notify.actors.add(sender) 
            notify.save()

post_save.connect(Stream.add_post, sender=Post)
post_save.connect(Likes.user_like_post, sender=Likes)
post_delete.connect(Likes.user_unlike_post, sender=Likes)
post_save.connect(Post.change_tag_slug, sender=Tag)
comment_was_posted.connect(user_comment_post, sender=Comment)
