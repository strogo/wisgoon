# -*- coding: utf8 -*- 

from django.db import models
from django.contrib.auth.models import User

class Post(models.Model):
    #title = models.CharField(max_length=250, blank=True)
    text = models.TextField(blank=True, verbose_name='متن')
    image = models.CharField(max_length=500, verbose_name='تصویر')
    create_date = models.DateField(auto_now_add=True)
    create = models.DateTimeField(auto_now_add=True)
    timestamp = models.IntegerField(db_index=True, default=1347546432)
    user = models.ForeignKey(User)
    like = models.IntegerField(default=0)
    
    def __unicode__(self):
        return self.text
    
    @models.permalink
    def get_absolute_url(self):
        return ('pin-item', [str(self.id)])
    
    