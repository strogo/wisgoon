# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


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
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='log',
            name='create_time',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='device',
            field=models.IntegerField(default=1, blank=True, choices=[(1, b'web'), (2, b'mobile version 2'), (3, b'mobile version 6')]),
        ),
        migrations.AlterField(
            model_name='post',
            name='image',
            field=models.CharField(max_length=500, verbose_name='Picture'),
        ),
        migrations.AlterField(
            model_name='post',
            name='is_ads',
            field=models.BooleanField(default=False, verbose_name='Advertisement'),
        ),
        migrations.AlterField(
            model_name='post',
            name='show_in_default',
            field=models.BooleanField(default=False, db_index=True, verbose_name='Show in Home'),
        ),
        migrations.AlterField(
            model_name='post',
            name='status',
            field=models.IntegerField(default=0, blank=True, verbose_name='Status', choices=[(0, 'Pending'), (1, 'Accepted'), (2, 'Violation')]),
        ),
    ]
