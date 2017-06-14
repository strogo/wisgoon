# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0028_profile_is_private'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='is_private',
            field=models.BooleanField(default=False, verbose_name='Private'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='name',
            field=models.CharField(max_length=250, null=True, verbose_name='Name', blank=True),
        ),
    ]
