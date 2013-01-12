# -*- coding: utf8 -*- 

from django.db import models
from django.contrib.auth.models import User

class Feed(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=1000, blank=True)
    last_fetch = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(default=1)
    creator = models.ForeignKey(User)
    followers = models.IntegerField(default=0)
    view = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    lock = models.BooleanField(default=False)
    
    def __unicode__(self):
        return self.url
    
    @models.permalink
    def get_absolute_url(self):
        return ('rss-feed', [str(self.id)])
    
class Item(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    url = models.URLField()
    url_crc = models.IntegerField()
    date = models.DateTimeField()
    timestamp = models.IntegerField(db_index=True)
    feed = models.ForeignKey(Feed)
    image = models.CharField(max_length=250, blank=True)
    goto = models.IntegerField(default=0)
    likes = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.title
    
    @models.permalink
    def get_absolute_url(self):
        return ('rss-item', [str(self.feed.id), str(self.id)])
        
    class Meta:
        unique_together = (("feed", "url_crc"),)
        
    
    
class Subscribe(models.Model):
    user = models.ForeignKey(User)
    feed = models.ForeignKey(Feed)
    
    class Meta:
        unique_together = (("feed", "user"),)
    
class Likes(models.Model):
    user = models.ForeignKey(User)
    item = models.ForeignKey(Item, related_name="post_item")
    
    class Meta:
        unique_together = (("item", "user"),)
    
class Report(models.Model):
    MODES = (
        (1, 'توهین به مقدسات'),
        (2, 'توهین به مسوولین'),
        (3, 'محتوای غیر اخلاقی'),
    )
    
    user = models.ForeignKey(User)
    item = models.ForeignKey(Item, related_name="report_item")
    mode = models.IntegerField(default=1,choices=MODES)
    
    class Meta:
        unique_together = (("item", "user"),)
        
        
   
class Search(models.Model):
    keyword=models.CharField(max_length=80, unique=True)
    slug=models.SlugField()
    accept=models.BooleanField()
    count=models.IntegerField(default=1)

    @models.permalink
    def to_url(self):
        return ('tag', [self.slug])
    
    def __unicode__(self):
        return self.keyword
    
    def save(self, *args, **kwargs):
        self.slug = '-'.join(self.keyword.split())#And clean title, and make sure this is unique.
        super(Search, self).save(*args, **kwargs)

class Lastview(models.Model):
    item = models.IntegerField(unique=True)

    