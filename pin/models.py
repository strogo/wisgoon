# -*- coding: utf8 -*- 

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from django.contrib.comments.signals import comment_was_posted
from django.core.validators import URLValidator
from django.contrib.sites.models import Site
from django.conf import settings
from taggit.managers import TaggableManager
from taggit.models import Tag
from django.contrib.comments.models import Comment

class Post(models.Model):
    #title = models.CharField(max_length=250, blank=True)
    text = models.TextField(blank=True, verbose_name='متن')
    image = models.CharField(max_length=500, verbose_name='تصویر')
    create_date = models.DateField(auto_now_add=True)
    create = models.DateTimeField(auto_now_add=True)
    timestamp = models.IntegerField(db_index=True, default=1347546432)
    user = models.ForeignKey(User)
    like = models.IntegerField(default=0)
    url = models.CharField(blank=True, max_length=2000, validators=[URLValidator()])
    
    tags = TaggableManager(blank=True)
    
    def __unicode__(self):
        return self.text
    
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

class Follow(models.Model):
    follower = models.ForeignKey(User ,related_name='follower')
    following = models.ForeignKey(User, related_name='following')

class Stream(models.Model):
    following = models.ForeignKey(User, related_name='stream_following')
    user = models.ForeignKey(User ,related_name='user')
    post = models.ForeignKey(Post)
    date = models.IntegerField(default=0)
    
class Likes(models.Model):
    user = models.ForeignKey(User,related_name='pin_post_user_like')
    post = models.ForeignKey(Post, related_name="post_item")
    
    class Meta:
        unique_together = (("post", "user"),)

class Notify(models.Model):
    TYPES = ((1,'like'),(2,'comment'))
    
    post = models.ForeignKey(Post)
    sender = models.ForeignKey(User, related_name="sender")
    user = models.ForeignKey(User, related_name="userid")
    text = models.CharField(max_length=500)
    seen = models.BooleanField(default=False)
    type = models.IntegerField(default=1, choices=TYPES) # 1=Post_like, 2=Post_comment

def add_post_to_stream(sender, **kwargs):
    post = kwargs['instance']
    user = post.user
    followers = Follow.objects.all().filter(following=user)
    for follower in followers:
        stream = Stream(post=post, user=follower.follower, date=post.timestamp, following=user)
        stream.save()

def user_like_post(sender, **kwargs):
    like = kwargs['instance']
    post = like.post
    sender = like.user
    
    notify = Notify()
    notify.post = post
    notify.sender = sender
    notify.user = post.user
    notify.text = 'like this'
    notify.save()
    
def user_unlike_post(sender, **kwargs):
    like = kwargs['instance']
    post = like.post
    sender = like.user
    
    notify = Notify.objects.all().filter(post=post, sender=sender)
    notify.delete()
    
def user_comment_post(sender, **kwargs):
    if 'pin.post' in kwargs['request'].POST['content_type']:
        comment = kwargs['comment']
        post_id = kwargs['request'].POST['object_pk']
        post = Post.objects.get(pk=post_id)
        if comment.user != post.user:
            #post = comment.post
            sender = comment.user
                
            notify = Notify()
            notify.post = post
            notify.sender = sender
            notify.user = post.user
            notify.text = 'comment this'
            notify.type = 2
            notify.save()
                
def change_tag_slug(sender, **kwargs):
    if kwargs['created']:
        tag = kwargs['instance']
        tag.slug = '-'.join(tag.name.split())#And clean title, and make sure this is unique.
        tag.save()

post_save.connect(add_post_to_stream, sender=Post)
post_save.connect(user_like_post, sender=Likes)
post_delete.connect(user_unlike_post, sender=Likes)
post_save.connect(change_tag_slug, sender=Tag)
comment_was_posted.connect(user_comment_post, sender=Comment)