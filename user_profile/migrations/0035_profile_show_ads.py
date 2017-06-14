# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0034_auto_20170111_1609'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='show_ads',
            field=models.BooleanField(default=True, verbose_name='Show ads'),
        ),
    ]
