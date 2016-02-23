# coding: utf-8
import os
import time

from PIL import Image, ImageOps

from datetime import datetime

from django.conf import settings
from django.core.cache import cache
from django.db import models
from django.db.models import F
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _

from pin.model_mongo import MonthlyStats
from pin.models_graph import UserGraph


def avatar_file_name(instance, filename):
    new_filename = str(time.time()).replace('.', '')
    fileext = os.path.splitext(filename)[1]
    if not fileext:
        fileext = '.jpg'

    filestr = new_filename + fileext
    d = datetime.now()
    avatars_prefix = "avatars/%s" % settings.INSTANCE_NAME
    return '/'.join([avatars_prefix, str(d.year), str(d.month), str(d.day), str(filestr)])


def cover_file_name(instance, filename):
    new_filename = str(time.time()).replace('.', '')
    fileext = os.path.splitext(filename)[1]
    if not fileext:
        fileext = '.jpg'

    filestr = new_filename + fileext
    d = datetime.now()
    avatars_prefix = "covers/%s" % settings.INSTANCE_NAME
    return '/'.join([avatars_prefix, str(d.year), str(d.month), str(d.day), str(filestr)])


class Profile(models.Model):

    AVATAR_OLD_STYLE = 0
    AVATAR_NEW_STYLE = 1
    AVATAT_MIGRATED = 2

    name = models.CharField(max_length=250, verbose_name=_("Name"))
    location = models.CharField(max_length=250, verbose_name=_("Location"),
                                blank=True)
    website = models.URLField(verbose_name=_('Website'), blank=True)
    bio = models.TextField(verbose_name=_('Biography'), blank=True)
    cnt_post = models.IntegerField(default=0)
    cnt_like = models.IntegerField(default=0)
    score = models.IntegerField(default=0, db_index=True)
    count_flag = models.IntegerField(default=0)
    trusted = models.IntegerField(default=0)
    trusted_by = models.ForeignKey(User, related_name='trusted_by',
                                   default=None, null=True, blank=True)
    avatar = models.ImageField(upload_to=avatar_file_name, default=None,
                               null=True, blank=True)
    cover = models.ImageField(upload_to=cover_file_name, default=None,
                              null=True, blank=True)
    jens = models.CharField(max_length=2,
                            choices=(('M', _('Male')), ('F', _('Female'))),
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

    credit = models.IntegerField(default=0)
    level = models.IntegerField(default=1)

    banned = models.BooleanField(default=False)

    version = models.IntegerField(default=0, blank=False, null=True)

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
        return self.credit

    def get_level_string(self):
        if self.level == 1:
            return _('Normal')
        elif self.level == 2:
            return _('Cop')

        self.level = 1
        self.save()
        return self.get_level_string()

    def is_police(self):
        if self.level == 2:
            return True
        return False

    def inc_credit(self, amount):
        CreditLog.objects.create(prof_id=self.id,
                                 mode=CreditLog.INCREMENT,
                                 amount=amount)

        Profile.objects.filter(id=self.id)\
            .update(credit=F('credit') + amount)

    def dec_credit(self, amount):
        CreditLog.objects.create(prof_id=self.id,
                                 mode=CreditLog.DECREMENT,
                                 amount=amount)

        Profile.objects.filter(id=self.id)\
            .update(credit=F('credit') - amount)

    @classmethod
    def after_like(cls, user_id):
        if settings.LIKE_WITH_CELERY:
            from pin.actions import send_profile_after_like
            send_profile_after_like(user_id=user_id)

            return

        Profile.objects.filter(user_id=user_id)\
            .update(cnt_like=F('cnt_like') + 1, score=F('score') + 10)

    @classmethod
    def after_dislike(cls, user_id):
        if settings.LIKE_WITH_CELERY:
            from pin.actions import send_profile_after_dislike
            send_profile_after_dislike(user_id=user_id)

            return

        Profile.objects.filter(user_id=user_id)\
            .update(cnt_like=F('cnt_like') - 1, score=F('score') - 10)

    def get_avatar_64_str(self):
        s = str(self.avatar)
        l = s.split('/')
        l[-1] = "%s_%s" % (64, l[-1])
        return '/'.join(l)

    def store_avatars(self, update_model=False):
        try:
            im = Image.open(self.avatar)
        except IOError, e:
            print str(e)
            return

        ipath = "%s/%s" % (settings.MEDIA_ROOT, self.avatar)
        idir = os.path.dirname(ipath)
        iname = os.path.basename(ipath)

        nname_64 = "64_%s" % (iname)
        npath_64 = "%s/%s" % (idir, nname_64)

        nname = "%s" % (iname)
        npath = "%s/%s" % (idir, nname)

        thumbnail_210 = ImageOps.fit(
            im,
            (210, 210),
            Image.ANTIALIAS
        )
        thumbnail_210.save(npath, format='JPEG')

        thumbnail_64 = ImageOps.fit(
            im,
            (64, 64),
            Image.ANTIALIAS
        )
        thumbnail_64.save(npath_64, format='JPEG')
        if update_model:
            self.version = Profile.AVATAR_NEW_STYLE
            self.save()

    def delete_avatar_cache(self):
        cache_key = settings.AVATAR_CACHE_KEY.format(self.user_id)
        cache.delete(cache_key)

    def save(self, *args, **kwargs):
        have_new_avatar = False
        try:
            this = Profile.objects.get(id=self.id)
            if this.avatar != self.avatar and '/' not in self.avatar:
                have_new_avatar = True
                self.version = self.AVATAR_NEW_STYLE
                ipath = "%s/%s" % (settings.MEDIA_ROOT, this.avatar)
                idir = os.path.dirname(ipath)
                iname = os.path.basename(ipath)
                nname_64 = "64_%s" % (iname)
                npath_64 = "%s/%s" % (idir, nname_64)
                os.remove(npath_64)
                this.avatar.delete(save=False)

        except Exception, e:
            print str(e)

        super(Profile, self).save(*args, **kwargs)

        if have_new_avatar:
            self.delete_avatar_cache()

            from pin.tasks import add_avatar_to_storage
            self.store_avatars(update_model=False)
            add_avatar_to_storage.delay(self.id)

        user_id = int(self.user_id)
        user_str = "user_name_%d" % (user_id)
        cache.delete(user_str)

        profile_str = "profile_name_%d" % (user_id)
        cache.delete(profile_str)

        new_avatar = "new_avatar_%d" % (user_id)
        cache.set(new_avatar, 1, 160000)


class CreditLog(models.Model):
    INCREMENT = 1
    DECREMENT = 2

    MODE_CHOICES = (
        (INCREMENT, _('Increment')),
        (DECREMENT, _('Decrement')),
    )

    # profile = models.ForeignKey(Profile, related_name="user_credit_log")
    prof_id = models.IntegerField(default=0)
    mode = models.IntegerField(blank=True, null=True, default=1,
                               choices=MODE_CHOICES)
    amount = models.IntegerField(default=0)
    create_time = models.DateTimeField(default=datetime.now())


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        MonthlyStats.log_hit(object_type=MonthlyStats.USER)

        profile, created = Profile.objects\
            .get_or_create(user=instance, name=instance.username)
        try:
            UserGraph.get_or_create("Person", instance.username,
                                    instance.profile.name, instance.id)
        except Exception as e:
            print str(e)

        try:
            instance.is_active = True
            instance.save()
        except Exception, e:
            pass

post_save.connect(create_user_profile, sender=User)
