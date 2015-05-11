# coding: utf-8
import os
import time
from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.db.models.signals import post_save


def avatar_file_name(instance, filename):
    new_filename = str(time.time()).replace('.', '')
    fileext = os.path.splitext(filename)[1]

    filestr = new_filename + fileext
    d = datetime.now()
    return '/'.join(['avatars', str(d.year), str(d.month), str(filestr)])


class Profile(models.Model):
    name = models.CharField(max_length=250, verbose_name='نام')
    location = models.CharField(max_length=250, verbose_name='موقعیت',
                                blank=True)
    website = models.URLField(verbose_name='وب سایت', blank=True)
    bio = models.TextField(verbose_name='توضیحات', blank=True)
    cnt_post = models.IntegerField(default=0)
    cnt_like = models.IntegerField(default=0)
    score = models.IntegerField(default=0, db_index=True)
    count_flag = models.IntegerField(default=0)
    trusted = models.IntegerField(default=0)
    trusted_by = models.ForeignKey(User, related_name='trusted_by',
                                   default=None, null=True, blank=True)
    avatar = models.ImageField(upload_to=avatar_file_name, default=None,
                               null=True, blank=True)
    jens = models.CharField(max_length=2,
                            choices=(('M', 'مذکر'), ('F', 'مونث')),
                            default='M')
    user = models.OneToOneField(User)

    fault = models.IntegerField(default=0, null=True, blank=True)
    fault_minus = models.IntegerField(default=0, null=True, blank=True)

    post_accept = models.BooleanField(default=False, blank=True)
    post_accept_admin = models.BooleanField(default=True, blank=True)
    email_active = models.BooleanField(default=False, blank=True)
    activation_key = models.CharField(max_length=50, default=0, blank=True)

    cnt_following = models.IntegerField(default=-1, blank=True, null=True)
    cnt_followers = models.IntegerField(default=-1, blank=True, null=True)

    credit = models.IntegerField(default=-1, blank=True, null=True)
    level = models.IntegerField(default=-1, blank=True, null=True)

    def get_cnt_following(self):
        if self.cnt_following == -1 or self.cnt_following is None:
            from pin.models import Follow
            cnt_following = Follow.objects.filter(follower_id=self.user_id)\
                .count()
            if cnt_following:
                Profile.objects.filter(id=self.id)\
                    .update(cnt_following=cnt_following)
        else:
            cnt_following = self.cnt_following

        return cnt_following

    def get_cnt_followers(self):
        if self.cnt_followers == -1 or self.cnt_followers is None:
            from pin.models import Follow
            cnt_followers = Follow.objects.filter(following_id=self.user_id)\
                .count()
            if cnt_followers:
                Profile.objects.filter(id=self.id)\
                    .update(cnt_followers=cnt_followers)
        else:
            cnt_followers = self.cnt_followers

        return cnt_followers

    def get_credit(self):
        if self.credit == -1 or self.credit is None:
            from pin.tools import get_user_meta
            um = get_user_meta(user_id=self.user_id)
            if um:
                Profile.objects.filter(id=self.id)\
                    .update(credit=um.credit)
            return um.credit
        else:
            return self.credit

    def get_level_string(self):
        if self.level == -1 or self.level is None:
            from pin.tools import get_user_meta
            um = get_user_meta(user_id=self.user_id)
            if um:
                Profile.objects.filter(id=self.id)\
                    .update(level=um.level)
            self.level = um.level

        if self.level == 1:
            return u'عادی'
        elif self.level == 2:
            return u'پلیس'

    def is_police(self):
        if self.level == -1 or self.level is None:
            from pin.tools import get_user_meta
            um = get_user_meta(user_id=self.user_id)
            if um:
                Profile.objects.filter(id=self.id)\
                    .update(level=um.level)
            self.level = um.level

        if self.level == 2:
            return True
        return False

    def inc_credit(self, amount):
        Profile.objects.filter(id=self.id)\
            .update(credit=F('credit') + amount)

    @classmethod
    def after_like(cls, user_id):
        if settings.LIKE_WITH_CELERY:
            from pin.tasks import send_profile_after_like
            send_profile_after_like(user_id=user_id)

            return

        Profile.objects.filter(user_id=user_id)\
            .update(cnt_like=F('cnt_like') + 1, score=F('score') + 10)

    @classmethod
    def after_dislike(cls, user_id):
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
