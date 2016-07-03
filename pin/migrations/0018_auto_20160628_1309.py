# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0017_auto_20160517_1128'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lable',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=250)),
            ],
        ),
        migrations.CreateModel(
            name='UserActivitiesSample',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserLikeActivities',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('score', models.PositiveIntegerField(default=0)),
                ('category', models.ForeignKey(to='pin.Category')),
                ('user_activity', models.ForeignKey(to='pin.UserActivitiesSample')),
            ],
        ),
        migrations.AddField(
            model_name='useractivitiessample',
            name='categories',
            field=models.ManyToManyField(to='pin.Category', through='pin.UserLikeActivities'),
        ),
        migrations.AddField(
            model_name='useractivitiessample',
            name='label',
            field=models.ForeignKey(to='pin.Lable'),
        ),
    ]
