# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-24 11:50
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0003_auto_20160124_1520'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instaaccount',
            name='lc',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 24, 15, 20, 41, 800425)),
        ),
        migrations.AlterField(
            model_name='log',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 1, 24, 15, 20, 41, 804268)),
        ),
    ]
