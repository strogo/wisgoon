# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0004_auto_20160420_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditlog',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 3, 17, 21, 46, 930425)),
        ),
    ]
