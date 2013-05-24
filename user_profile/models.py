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
    
    def cnt_calculate(self):
        cnt = Post.objects.filter(user=self.user,status=1).aggregate(models.Sum('like'), models.Count('id'))
        
        self.cnt_like = 0 if not cnt['like__sum'] else cnt['like__sum']
        self.cnt_post = cnt['id__count']
        
    def score_calculation(self):
        score = self.cnt_post + (self.cnt_like * 10 )
        return score

    def user_statics(self):
        self.cnt_calculate()
        self.score = self.score_calculation()                                   
        self.count_flag = 1

    def save(self, *args, **kwargs):
        self.user_statics()

        super(Profile, self).save(*args,**kwargs)
