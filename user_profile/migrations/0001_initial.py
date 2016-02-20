# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import user_profile.models
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('prof_id', models.IntegerField(default=0)),
                ('mode', models.IntegerField(default=1, null=True, blank=True, choices=[(1, b'Increment'), (2, b'Decrement')])),
                ('amount', models.IntegerField(default=0)),
                ('create_time', models.DateTimeField(default=datetime.datetime(2016, 2, 16, 10, 49, 25, 328964))),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250, verbose_name=b'\xd9\x86\xd8\xa7\xd9\x85')),
                ('location', models.CharField(max_length=250, verbose_name=b'\xd9\x85\xd9\x88\xd9\x82\xd8\xb9\xdb\x8c\xd8\xaa', blank=True)),
                ('website', models.URLField(verbose_name=b'\xd9\x88\xd8\xa8 \xd8\xb3\xd8\xa7\xdb\x8c\xd8\xaa', blank=True)),
                ('bio', models.TextField(verbose_name=b'\xd8\xaa\xd9\x88\xd8\xb6\xdb\x8c\xd8\xad\xd8\xa7\xd8\xaa', blank=True)),
                ('cnt_post', models.IntegerField(default=0)),
                ('cnt_like', models.IntegerField(default=0)),
                ('score', models.IntegerField(default=0, db_index=True)),
                ('count_flag', models.IntegerField(default=0)),
                ('trusted', models.IntegerField(default=0)),
                ('avatar', models.ImageField(default=None, null=True, upload_to=user_profile.models.avatar_file_name, blank=True)),
                ('cover', models.ImageField(default=None, null=True, upload_to=user_profile.models.cover_file_name, blank=True)),
                ('jens', models.CharField(default=b'M', max_length=2, choices=[(b'M', b'\xd9\x85\xd8\xb0\xda\xa9\xd8\xb1'), (b'F', b'\xd9\x85\xd9\x88\xd9\x86\xd8\xab')])),
                ('fault', models.IntegerField(default=0, null=True, blank=True)),
                ('fault_minus', models.IntegerField(default=0, null=True, blank=True)),
                ('post_accept', models.BooleanField(default=False)),
                ('post_accept_admin', models.BooleanField(default=True)),
                ('email_active', models.BooleanField(default=False)),
                ('activation_key', models.CharField(default=0, max_length=50, blank=True)),
                ('cnt_following', models.IntegerField(default=-1, null=True, blank=True)),
                ('cnt_followers', models.IntegerField(default=-1, null=True, blank=True)),
                ('credit', models.IntegerField(default=0)),
                ('level', models.IntegerField(default=1)),
                ('banned', models.BooleanField(default=False)),
                ('version', models.IntegerField(default=0, null=True)),
                ('trusted_by', models.ForeignKey(related_name='trusted_by', default=None, blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
