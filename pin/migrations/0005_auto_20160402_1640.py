# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0004_merge'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instaaccount',
            name='insta_id',
            field=models.BigIntegerField(),
        ),
        migrations.AlterField(
            model_name='instaaccount',
            name='lc',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 2, 16, 40, 48, 405502)),
        ),
    ]
