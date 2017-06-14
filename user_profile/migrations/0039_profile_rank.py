# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0038_auto_20170116_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='rank',
            field=models.IntegerField(default=0, db_index=True),
        ),
    ]
