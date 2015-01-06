#coding: utf-8
import os
import time
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.db.models.signals import post_save

from pin.models import Post


def avatar_file_name(instance, filename):
    new_filename = str(time.time()).replace('.', '')
    fileext = os.path.splitext(filename)[1]

    filestr = new_filename + fileext
    d = datetime.now()
    return '/'.join(['avatars', str(d.year), str(d.month), str(filestr)])


class Profile(models.Model):
    name = models.CharField(max_length=250, verbose_name='نام')
    location = models.CharField(max_length=250, verbose_name='موقعیت', blank=True)
    website = models.URLField(verbose_name='وب سایت', blank=True)
    bio = models.TextField(verbose_name='توضیحات', blank=True)
    cnt_post = models.IntegerField(default=0)
    cnt_like = models.IntegerField(default=0)
    score = models.IntegerField(default=0, db_index=True)
    count_flag = models.IntegerField(default=0)
    trusted = models.IntegerField(default=0)
    trusted_by = models.ForeignKey(User, related_name='trusted_by', default=None, null=True, blank=True)
    avatar = models.ImageField(upload_to=avatar_file_name, default=None, null=True, blank=True)
    jens = models.CharField(max_length=2, choices=(('M', 'مذکر'), ('F', 'مونث')), default='M')
    user = models.OneToOneField(User)

    fault = models.IntegerField(default=0, null=True, blank=True)
    fault_minus = models.IntegerField(default=0, null=True, blank=True)

    post_accept = models.BooleanField(default=False, blank=True)
    post_accept_admin = models.BooleanField(default=True, blank=True)
    email_active = models.BooleanField(default=False, blank=True)
    activation_key = models.CharField(max_length=50, default=0, blank=True)

    # def cnt_calculate(self):
    #     try:
    #         cnt = Post.objects.filter(user=self.user, status=1).aggregate(models.Sum('cnt_like'), models.Count('id'))
    #     except Post.DoesNotExist:
    #         cnt = 0

    #     self.cnt_like = 0 if not cnt['cnt_like__sum'] else cnt['cnt_like__sum']
    #     self.cnt_post = cnt['id__count']

    # def score_calculation(self):
    #     score = self.cnt_post + (self.cnt_like * 10)
    #     #if self.trusted != 0:
    #     #    score = score+10000
    #     return score

    # def user_statics(self):
    #     # self.cnt_calculate()
    #     self.score = self.score_calculation()
    #     # self.count_flag = 1

    @classmethod
    def after_like(self, user_id):
        if settings.LIKE_WITH_CELERY:
            from pin.tasks import send_profile_after_like
            send_profile_after_like(user_id=user_id)

            return

        Profile.objects.filter(user_id=user_id)\
            .update(cnt_like=F('cnt_like') + 1, score=F('score') + 10)

    @classmethod
    def after_dislike(self, user_id):
        if settings.LIKE_WITH_CELERY:
            from pin.tasks import send_profile_after_dislike
            send_profile_after_dislike(user_id=user_id)
            
            return

        Profile.objects.filter(user_id=user_id)\
            .update(cnt_like=F('cnt_like') - 1, score=F('score') - 10)

    def save(self, *args, **kwargs):
        super(Profile, self).save(*args, **kwargs)
        user_id = int(self.user_id)
        user_str = "user_name_%d" % (user_id)
        cache.delete(user_str)

        profile_str = "profile_name_%d" % (user_id)
        cache.delete(profile_str)

        new_avatar = "new_avatar_%d" % (user_id)
        cache.set(new_avatar, 1, 160000)

        ava_str = "avatar3210u_%d" % (user_id)
        cache.delete(ava_str)


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        profile, created = Profile.objects.get_or_create(user=instance)

post_save.connect(create_user_profile, sender=User)
