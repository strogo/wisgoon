#coding: utf-8
from django.db import models
from django.contrib.auth.models import User

from pin.models import Post

class Profile(models.Model):
    name=models.CharField(max_length=250,verbose_name='نام')
    location=models.CharField(max_length=250, verbose_name='موقعیت', blank=True)
    website=models.URLField(verbose_name='وب سایت', blank=True)
    bio=models.TextField(verbose_name='توضیحات', blank=True)
    user=models.ForeignKey(User)
    cnt_post=models.IntegerField(default=0)
    cnt_like=models.IntegerField(default=0)
    score=models.IntegerField(default=0)
    count_flag=models.IntegerField(default=0)
    
    def cnt_post_calculate(self):
        cnt_post = Post.objects.filter(user=self.user,status=1).count()
        return cnt_post

    def cnt_like_calculate(self):
        cnt_like = Post.objects.filter(user=self.user,status=1).aggregate(models.Sum('like'))
        return cnt_like['like__sum']

    def score_calculation(self):
        score = self.cnt_post + (self.cnt_like * 10 )
        return score

    def user_statics(self):
        self.cnt_post = self.cnt_post_calculate()                               
        self.cnt_like = self.cnt_like_calculate()                               
        self.score = self.score_calculation()                                   
        self.count_flag = 1

    def save(self, *args, **kwargs):
        self.user_statics()

        super(Profile, self).save(*args,**kwargs)
