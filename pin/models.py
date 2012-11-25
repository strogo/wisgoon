# -*- coding: utf8 -*- 

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete

class Post(models.Model):
    #title = models.CharField(max_length=250, blank=True)
    text = models.TextField(blank=True, verbose_name='متن')
    image = models.CharField(max_length=500, verbose_name='تصویر')
    create_date = models.DateField(auto_now_add=True)
    create = models.DateTimeField(auto_now_add=True)
    timestamp = models.IntegerField(db_index=True, default=1347546432)
    user = models.ForeignKey(User)
    like = models.IntegerField(default=0)
    url = models.URLField(blank=True)
    
    def __unicode__(self):
        return self.text
    
    @models.permalink
    def get_absolute_url(self):
        return ('pin-item', [str(self.id)])
    
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
    post = models.ForeignKey(Post)
    sender = models.ForeignKey(User, related_name="sender")
    user = models.ForeignKey(User, related_name="userid")
    text = models.CharField(max_length=500)
    seen = models.BooleanField(default=False)
    type = models.IntegerField(default=1) # 1=Post_like, 2=Post_comment

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

post_save.connect(add_post_to_stream, sender=Post)
post_save.connect(user_like_post, sender=Likes)
post_delete.connect(user_unlike_post, sender=Likes)