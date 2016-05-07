# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0013_userlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='userlog',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 5, 7, 7, 50, 16, 518539, tzinfo=utc), auto_now=True),
            preserve_default=False,
        ),
    ]
