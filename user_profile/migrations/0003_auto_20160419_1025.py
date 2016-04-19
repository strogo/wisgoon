# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0002_auto_20160405_1013'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditlog',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 19, 10, 25, 50, 182841)),
        ),
    ]
