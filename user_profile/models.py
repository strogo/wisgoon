#coding: utf-8
import os
import time
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from pin.models import Post

def avatar_file_name(instance, filename):
    new_filename = str(time.time()).replace('.','') # create new file name with current timestamp
    fileext = os.path.splitext(filename)[1] # get file ext

    filestr = new_filename + fileext 
    
    d = datetime.now()
    return '/'.join(['avatars', str(d.year), str(d.month), str(filestr)])

class Profile(models.Model):
    name=models.CharField(max_length=250,verbose_name='نام')
    location=models.CharField(max_length=250, verbose_name='موقعیت', blank=True)
    website=models.URLField(verbose_name='وب سایت', blank=True)
    bio=models.TextField(verbose_name='توضیحات', blank=True)
    cnt_post=models.IntegerField(default=0)
    cnt_like=models.IntegerField(default=0)
    score=models.IntegerField(default=0, db_index=True)
    count_flag=models.IntegerField(default=0)
    trusted=models.IntegerField(default=0)
    trusted_by=models.ForeignKey(User, related_name='trusted_by', default=None, null=True, blank=True)
    avatar = models.ImageField(upload_to=avatar_file_name, default=None, null=True, blank=True)

    user = models.OneToOneField(User)

    
    def cnt_calculate(self):
        cnt = Post.objects.filter(user=self.user,status=1).aggregate(models.Sum('like'), models.Count('id'))
        
        self.cnt_like = 0 if not cnt['like__sum'] else cnt['like__sum']
        self.cnt_post = cnt['id__count']
        
    def score_calculation(self):
        score = self.cnt_post + (self.cnt_like * 10 )
        #if self.trusted != 0:
        #    score = score+10000
        return score

    def user_statics(self):
        self.cnt_calculate()
        self.score = self.score_calculation()                                   
        self.count_flag = 1

    def save(self, *args, **kwargs):
        self.user_statics()

        super(Profile, self).save(*args,**kwargs)

def create_user_profile(sender, instance, created, **kwargs):  
    if created:  
       profile, created = Profile.objects.get_or_create(user=instance)  

post_save.connect(create_user_profile, sender=User)
