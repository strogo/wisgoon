# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ended', models.BooleanField(default=False, db_index=True)),
                ('cnt_view', models.IntegerField(default=0)),
                ('ads_type', models.IntegerField(default=1)),
                ('start', models.DateTimeField(auto_now=True)),
                ('end', models.DateTimeField(null=True, blank=True)),
                ('ip_address', models.GenericIPAddressField(default=b'127.0.0.1')),
                ('owner', models.ForeignKey(related_name='owner', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='App_data',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=250)),
                ('file', models.FileField(upload_to=b'app')),
                ('version', models.CharField(max_length=50)),
                ('version_code', models.IntegerField(default=0, blank=True)),
                ('current', models.BooleanField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='BannedImei',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('imei', models.CharField(max_length=50, db_index=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(default=b'')),
                ('user', models.ForeignKey(default=1, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Bills2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.IntegerField(default=0, null=True, blank=True, choices=[(1, b'Completed'), (0, b'Uncompleted'), (2, b'Fakery'), (3, b'validate error'), (4, b'not valid')])),
                ('amount', models.IntegerField(null=True, blank=True)),
                ('trans_id', models.CharField(db_index=True, max_length=250, null=True, blank=True)),
                ('create_date', models.DateField(default=datetime.datetime.now)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('blocked', models.ForeignKey(related_name='blocked', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='blocker', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('image', models.ImageField(default=b'', upload_to=b'pin/category/')),
            ],
        ),
        migrations.CreateModel(
            name='CommentClassification',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CommentClassificationTags',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('comment', models.TextField()),
                ('submit_date', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(default=b'127.0.0.1', db_index=True)),
                ('is_public', models.BooleanField(default=False, db_index=True)),
                ('reported', models.BooleanField(default=False, db_index=True)),
                ('score', models.IntegerField(default=0, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Comments_score',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.IntegerField(default=0, blank=True)),
                ('comment', models.ForeignKey(to='pin.Comments')),
                ('user', models.ForeignKey(related_name='comment_like_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('follower', models.ForeignKey(related_name='follower', to=settings.AUTH_USER_MODEL)),
                ('following', models.ForeignKey(related_name='following', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InstaAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('insta_id', models.IntegerField()),
                ('lc', models.DateTimeField(default=datetime.datetime(2016, 2, 16, 10, 49, 25, 320117))),
                ('cat', models.ForeignKey(to='pin.Category')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ip', models.GenericIPAddressField(default=b'127.0.0.1')),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('action', models.IntegerField(default=1, db_index=True, choices=[(1, b'delete'), (2, b'pending'), (3, b'bad comment'), (4, b'bad post'), (5, b'ban imei'), (6, b'ban by admin'), (7, b'activated')])),
                ('object_id', models.IntegerField(default=0, db_index=True)),
                ('content_type', models.IntegerField(default=1, db_index=True, choices=[(1, b'post'), (2, b'comment'), (3, b'user'), (4, b'comment test')])),
                ('ip_address', models.GenericIPAddressField(default=b'127.0.0.1', db_index=True)),
                ('owner', models.IntegerField(default=0)),
                ('text', models.TextField(default=b'', null=True, blank=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime(2016, 2, 16, 10, 49, 25, 322829))),
                ('post_image', models.CharField(max_length=250, null=True, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notif',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=500)),
                ('seen', models.BooleanField(default=False)),
                ('type', models.IntegerField(default=1, choices=[(1, b'like'), (2, b'comment'), (3, b'approve'), (4, b'fault')])),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notif_actors',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('actor', models.ForeignKey(related_name='actor', to=settings.AUTH_USER_MODEL)),
                ('notif', models.ForeignKey(related_name='notif', to='pin.Notif')),
            ],
        ),
        migrations.CreateModel(
            name='Notifbar',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('seen', models.BooleanField(default=False)),
                ('type', models.IntegerField(default=1, choices=[(1, b'like'), (2, b'comment'), (3, b'approve'), (4, b'fault')])),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(related_name='actor_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Official',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('mode', models.IntegerField(default=b'1', choices=[(1, b'sp1'), (2, b'sp2')])),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Packages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('name', models.CharField(max_length=250)),
                ('wis', models.IntegerField(default=0)),
                ('price', models.IntegerField(default=0)),
                ('icon', models.ImageField(upload_to=b'packages/')),
            ],
        ),
        migrations.CreateModel(
            name='PhoneData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('imei', models.CharField(max_length=50)),
                ('os', models.CharField(max_length=50)),
                ('phone_model', models.CharField(max_length=50)),
                ('phone_serial', models.CharField(max_length=50)),
                ('android_version', models.CharField(max_length=20)),
                ('app_version', models.CharField(max_length=10)),
                ('google_token', models.CharField(max_length=500)),
                ('logged_out', models.BooleanField(default=False)),
                ('hash_data', models.CharField(default=b'', max_length=32)),
                ('user', models.OneToOneField(related_name='phone', null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(verbose_name='Text', blank=True)),
                ('image', models.CharField(max_length=500, verbose_name=b'\xd8\xaa\xd8\xb5\xd9\x88\xdb\x8c\xd8\xb1')),
                ('create_date', models.DateField(auto_now_add=True)),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('timestamp', models.IntegerField(default=1347546432, db_index=True)),
                ('like', models.IntegerField(default=0)),
                ('url', models.CharField(blank=True, max_length=2000, validators=[django.core.validators.URLValidator()])),
                ('status', models.IntegerField(default=0, blank=True, verbose_name=b'\xd9\x88\xd8\xb6\xd8\xb9\xdb\x8c\xd8\xaa', choices=[(0, b'\xd9\x85\xd9\x86\xd8\xaa\xd8\xb8\xd8\xb1 \xd8\xaa\xd8\xa7\xdb\x8c\xdb\x8c\xd8\xaf'), (1, b'\xd8\xaa\xd8\xa7\xdb\x8c\xdb\x8c\xd8\xaf \xd8\xb4\xd8\xaf\xd9\x87'), (2, b'\xd8\xaa\xd8\xae\xd9\x84\xd9\x81')])),
                ('device', models.IntegerField(default=1, blank=True)),
                ('hash', models.CharField(db_index=True, max_length=32, blank=True)),
                ('actions', models.IntegerField(default=1, blank=True)),
                ('is_ads', models.BooleanField(default=False, verbose_name=b'\xd8\xa2\xda\xaf\xd9\x87\xdb\x8c')),
                ('view', models.IntegerField(default=0, db_index=True)),
                ('show_in_default', models.BooleanField(default=False, db_index=True, verbose_name=b'\xd9\x86\xd9\x85\xd8\xa7\xdb\x8c\xd8\xb4 \xd8\xaf\xd8\xb1 \xd8\xae\xd8\xa7\xd9\x86\xd9\x87')),
                ('report', models.IntegerField(default=0, db_index=True)),
                ('cnt_comment', models.IntegerField(default=0, blank=True)),
                ('cnt_like', models.IntegerField(default=0, blank=True)),
                ('height', models.IntegerField(default=-1, blank=True)),
                ('width', models.IntegerField(default=-1, blank=True)),
                ('category', models.ForeignKey(default=1, verbose_name=b'\xda\xaf\xd8\xb1\xd9\x88\xd9\x87', to='pin.Category')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PostMetaData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('original_size', models.IntegerField(default=0)),
                ('status', models.IntegerField(default=1, db_index=True, choices=[(1, b'created'), (2, b'full image create'), (3, b'error in original image'), (4, b'redis server change')])),
                ('img_236_h', models.IntegerField(default=0)),
                ('img_500_h', models.IntegerField(default=0)),
                ('img_236', models.CharField(max_length=250)),
                ('img_500', models.CharField(max_length=250)),
                ('post', models.OneToOneField(to='pin.Post')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post', models.ForeignKey(related_name='report_post', to='pin.Post')),
                ('user', models.ForeignKey(related_name='report_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('label', models.CharField(max_length=250)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Sim',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('features', models.TextField()),
                ('post', models.OneToOneField(to='pin.Post')),
            ],
        ),
        migrations.CreateModel(
            name='Storages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('used', models.BigIntegerField(default=0)),
                ('num_files', models.IntegerField(default=0)),
                ('path', models.CharField(max_length=250)),
                ('host', models.CharField(max_length=100)),
                ('user', models.CharField(max_length=30)),
            ],
        ),
        migrations.CreateModel(
            name='Stream',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.IntegerField(default=0)),
                ('following', models.ForeignKey(related_name='stream_following', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(to='pin.Post')),
                ('user', models.ForeignKey(related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('image', models.ImageField(default=b'', upload_to=b'pin/scategory/')),
                ('image_device', models.ImageField(default=b'', upload_to=b'pin/scategory/')),
            ],
        ),
        migrations.AddField(
            model_name='notifbar',
            name='post',
            field=models.ForeignKey(to='pin.Post'),
        ),
        migrations.AddField(
            model_name='notifbar',
            name='user',
            field=models.ForeignKey(related_name='post_user_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notif',
            name='post',
            field=models.ForeignKey(to='pin.Post'),
        ),
        migrations.AddField(
            model_name='notif',
            name='user',
            field=models.ForeignKey(related_name='user_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='likes',
            name='post',
            field=models.ForeignKey(related_name='post_item', to='pin.Post'),
        ),
        migrations.AddField(
            model_name='likes',
            name='user',
            field=models.ForeignKey(related_name='pin_post_user_like', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comments',
            name='object_pk',
            field=models.ForeignKey(related_name='comment_post', to='pin.Post'),
        ),
        migrations.AddField(
            model_name='comments',
            name='user',
            field=models.ForeignKey(related_name='comment_sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentclassification',
            name='tag',
            field=models.ForeignKey(to='pin.CommentClassificationTags'),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(related_name='sub_category', blank=True, to='pin.SubCategory', null=True),
        ),
        migrations.AddField(
            model_name='ad',
            name='post',
            field=models.ForeignKey(to='pin.Post'),
        ),
        migrations.AddField(
            model_name='ad',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='stream',
            unique_together=set([('following', 'user', 'post')]),
        ),
        migrations.AlterUniqueTogether(
            name='report',
            unique_together=set([('post', 'user')]),
        ),
        migrations.AlterUniqueTogether(
            name='likes',
            unique_together=set([('post', 'user')]),
        ),
    ]
