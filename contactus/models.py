# encoding: utf-8
from django.db import models

class Feedback(models.Model):
    name = models.CharField(max_length=250, blank=True, verbose_name='نام')
    email = models.EmailField(verbose_name='ایمیل', blank=True)
    website = models.URLField(verbose_name='وب سایت', blank=True)
    text = models.TextField(verbose_name='متن پیام')