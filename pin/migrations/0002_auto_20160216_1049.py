# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instaaccount',
            name='lc',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 16, 10, 49, 47, 963246)),
        ),
        migrations.AlterField(
            model_name='log',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 16, 10, 49, 47, 965978)),
        ),
    ]
