# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-09 14:01
from __future__ import unicode_literals

import datetime
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ended', models.BooleanField(db_index=True, default=False)),
                ('cnt_view', models.IntegerField(default=0)),
                ('ads_type', models.IntegerField(default=1)),
                ('start', models.DateTimeField(auto_now=True)),
                ('end', models.DateTimeField(blank=True, null=True)),
                ('ip_address', models.GenericIPAddressField(default=b'127.0.0.1')),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='owner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='App_data',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=250)),
                ('file', models.FileField(upload_to=b'app')),
                ('version', models.CharField(max_length=50)),
                ('version_code', models.IntegerField(blank=True, default=0)),
                ('current', models.BooleanField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='BannedImei',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(db_index=True, max_length=50)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('description', models.TextField(default=b'')),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Bills2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.IntegerField(blank=True, choices=[(1, b'Completed'), (0, b'Uncompleted'), (2, b'Fakery'), (3, b'validate error'), (4, b'not valid')], default=0, null=True)),
                ('amount', models.IntegerField(blank=True, null=True)),
                ('trans_id', models.CharField(blank=True, db_index=True, max_length=250, null=True)),
                ('create_date', models.DateField(default=datetime.datetime.now)),
                ('create_time', models.DateTimeField(default=datetime.datetime.now)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blocked', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocked', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocker', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('image', models.ImageField(default=b'', upload_to=b'pin/category/')),
            ],
        ),
        migrations.CreateModel(
            name='CommentClassification',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='CommentClassificationTags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Comments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField()),
                ('submit_date', models.DateTimeField(auto_now_add=True)),
                ('ip_address', models.GenericIPAddressField(db_index=True, default=b'127.0.0.1')),
                ('is_public', models.BooleanField(db_index=True, default=False)),
                ('reported', models.BooleanField(db_index=True, default=False)),
                ('score', models.IntegerField(blank=True, default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Comments_score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.IntegerField(blank=True, default=0)),
                ('comment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pin.Comments')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_like_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('follower', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL)),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='InstaAccount',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('insta_id', models.IntegerField()),
                ('lc', models.DateTimeField(default=datetime.datetime(2016, 2, 9, 17, 31, 34, 947074))),
                ('cat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pin.Category')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Likes',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField(default=b'127.0.0.1')),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.IntegerField(choices=[(1, b'delete'), (2, b'pending'), (3, b'bad comment'), (4, b'bad post'), (5, b'ban imei'), (6, b'ban by admin'), (7, b'activated')], db_index=True, default=1)),
                ('object_id', models.IntegerField(db_index=True, default=0)),
                ('content_type', models.IntegerField(choices=[(1, b'post'), (2, b'comment'), (3, b'user'), (4, b'comment test')], db_index=True, default=1)),
                ('ip_address', models.GenericIPAddressField(db_index=True, default=b'127.0.0.1')),
                ('owner', models.IntegerField(default=0)),
                ('text', models.TextField(blank=True, default=b'', null=True)),
                ('create_time', models.DateTimeField(default=datetime.datetime(2016, 2, 9, 17, 31, 34, 950973))),
                ('post_image', models.CharField(blank=True, max_length=250, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Notif',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(max_length=500)),
                ('seen', models.BooleanField(default=False)),
                ('type', models.IntegerField(choices=[(1, b'like'), (2, b'comment'), (3, b'approve'), (4, b'fault')], default=1)),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Notif_actors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actor', to=settings.AUTH_USER_MODEL)),
                ('notif', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notif', to='pin.Notif')),
            ],
        ),
        migrations.CreateModel(
            name='Notifbar',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('seen', models.BooleanField(default=False)),
                ('type', models.IntegerField(choices=[(1, b'like'), (2, b'comment'), (3, b'approve'), (4, b'fault')], default=1)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='actor_id', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Official',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mode', models.IntegerField(choices=[(1, b'sp1'), (2, b'sp2')], default=b'1')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Packages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('imei', models.CharField(max_length=50)),
                ('os', models.CharField(max_length=50)),
                ('phone_model', models.CharField(max_length=50)),
                ('phone_serial', models.CharField(max_length=50)),
                ('android_version', models.CharField(max_length=20)),
                ('app_version', models.CharField(max_length=10)),
                ('google_token', models.CharField(max_length=500)),
                ('logged_out', models.BooleanField(default=False)),
                ('hash_data', models.CharField(default=b'', max_length=32)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='phone', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(blank=True, verbose_name='Text')),
                ('image', models.CharField(max_length=500, verbose_name=b'\xd8\xaa\xd8\xb5\xd9\x88\xdb\x8c\xd8\xb1')),
                ('create_date', models.DateField(auto_now_add=True)),
                ('create', models.DateTimeField(auto_now_add=True)),
                ('timestamp', models.IntegerField(db_index=True, default=1347546432)),
                ('like', models.IntegerField(default=0)),
                ('url', models.CharField(blank=True, max_length=2000, validators=[django.core.validators.URLValidator()])),
                ('status', models.IntegerField(blank=True, choices=[(0, b'\xd9\x85\xd9\x86\xd8\xaa\xd8\xb8\xd8\xb1 \xd8\xaa\xd8\xa7\xdb\x8c\xdb\x8c\xd8\xaf'), (1, b'\xd8\xaa\xd8\xa7\xdb\x8c\xdb\x8c\xd8\xaf \xd8\xb4\xd8\xaf\xd9\x87'), (2, b'\xd8\xaa\xd8\xae\xd9\x84\xd9\x81')], default=0, verbose_name=b'\xd9\x88\xd8\xb6\xd8\xb9\xdb\x8c\xd8\xaa')),
                ('device', models.IntegerField(blank=True, default=1)),
                ('hash', models.CharField(blank=True, db_index=True, max_length=32)),
                ('actions', models.IntegerField(blank=True, default=1)),
                ('is_ads', models.BooleanField(default=False, verbose_name=b'\xd8\xa2\xda\xaf\xd9\x87\xdb\x8c')),
                ('view', models.IntegerField(db_index=True, default=0)),
                ('show_in_default', models.BooleanField(db_index=True, default=False, verbose_name=b'\xd9\x86\xd9\x85\xd8\xa7\xdb\x8c\xd8\xb4 \xd8\xaf\xd8\xb1 \xd8\xae\xd8\xa7\xd9\x86\xd9\x87')),
                ('report', models.IntegerField(db_index=True, default=0)),
                ('cnt_comment', models.IntegerField(blank=True, default=0)),
                ('cnt_like', models.IntegerField(blank=True, default=0)),
                ('height', models.IntegerField(blank=True, default=-1)),
                ('width', models.IntegerField(blank=True, default=-1)),
                ('category', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='pin.Category', verbose_name=b'\xda\xaf\xd8\xb1\xd9\x88\xd9\x87')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='PostMetaData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('original_size', models.IntegerField(default=0)),
                ('status', models.IntegerField(choices=[(1, b'created'), (2, b'full image create'), (3, b'error in original image'), (4, b'redis server change')], db_index=True, default=1)),
                ('img_236_h', models.IntegerField(default=0)),
                ('img_500_h', models.IntegerField(default=0)),
                ('img_236', models.CharField(max_length=250)),
                ('img_500', models.CharField(max_length=250)),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pin.Post')),
            ],
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_post', to='pin.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='report_user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=250)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Sim',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('features', models.TextField()),
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='pin.Post')),
            ],
        ),
        migrations.CreateModel(
            name='Storages',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.IntegerField(default=0)),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stream_following', to=settings.AUTH_USER_MODEL)),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pin.Post')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SubCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('image', models.ImageField(default=b'', upload_to=b'pin/scategory/')),
            ],
        ),
        migrations.AddField(
            model_name='notifbar',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pin.Post'),
        ),
        migrations.AddField(
            model_name='notifbar',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_user_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='notif',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pin.Post'),
        ),
        migrations.AddField(
            model_name='notif',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_id', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='likes',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='post_item', to='pin.Post'),
        ),
        migrations.AddField(
            model_name='likes',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pin_post_user_like', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='comments',
            name='object_pk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_post', to='pin.Post'),
        ),
        migrations.AddField(
            model_name='comments',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comment_sender', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='commentclassification',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pin.CommentClassificationTags'),
        ),
        migrations.AddField(
            model_name='category',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sub_category', to='pin.SubCategory'),
        ),
        migrations.AddField(
            model_name='ad',
            name='post',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pin.Post'),
        ),
        migrations.AddField(
            model_name='ad',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
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
