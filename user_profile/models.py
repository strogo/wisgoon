#coding: utf-8
from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    name=models.CharField(max_length=250,verbose_name='نام')
    location=models.CharField(max_length=250, verbose_name='موقعیت', blank=True)
    website=models.URLField(verbose_name='وب سایت', blank=True)
    bio=models.TextField(verbose_name='توضیحات', blank=True)
    user=models.ForeignKey(User)
