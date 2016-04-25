# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='creditlog',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 4, 5, 10, 13, 20, 226604)),
        ),
        migrations.AlterField(
            model_name='profile',
            name='bio',
            field=models.TextField(verbose_name='Biography', blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='jens',
            field=models.CharField(default=b'M', max_length=2, choices=[(b'M', 'Male'), (b'F', 'Female')]),
        ),
        migrations.AlterField(
            model_name='profile',
            name='location',
            field=models.CharField(max_length=250, verbose_name='Location', blank=True),
        ),
        migrations.AlterField(
            model_name='profile',
            name='name',
            field=models.CharField(max_length=250, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='profile',
            name='website',
            field=models.URLField(verbose_name='Website', blank=True),
        ),
    ]
