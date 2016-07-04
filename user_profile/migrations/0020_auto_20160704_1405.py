# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0019_auto_20160629_1509'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditlog',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 7, 4, 14, 5, 50, 865110)),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cnt_followers',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='cnt_following',
            field=models.IntegerField(default=0, null=True, blank=True),
        ),
    ]
