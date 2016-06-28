# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0009_auto_20160628_1243'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditlog',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 6, 28, 13, 9, 22, 79016)),
        ),
    ]
