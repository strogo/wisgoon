from django.db import models
from django.contrib.auth.models import User

class Feed(models.Model):
    url = models.URLField()
    title = models.CharField(max_length=500, blank=True)
    last_fetch = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(default=1)
    creator = models.ForeignKey(User)
    followers = models.IntegerField(default=0)
    view = models.IntegerField(default=0)
    status = models.IntegerField(default=1)
    
    def __unicode__(self):
        return self.url
    
class Item(models.Model):
    title = models.CharField(max_length=250)
    description = models.TextField()
    url = models.URLField()
    url_crc = models.IntegerField()
    date = models.DateTimeField()
    timestamp = models.IntegerField(db_index=True)
    feed = models.ForeignKey(Feed)
    
    def __unicode__(self):
        return self.title
    
    class Meta:
        unique_together = (("feed", "url_crc"),)
    
class Subscribe(models.Model):
    user = models.ForeignKey(User)
    feed = models.ForeignKey(Feed)
    
    class Meta:
        unique_together = (("feed", "user"),)
    