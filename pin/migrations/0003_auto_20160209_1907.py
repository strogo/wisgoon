# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-02-09 15:37
from __future__ import unicode_literals

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0002_auto_20160209_1905'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instaaccount',
            name='lc',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 9, 19, 7, 7, 924694)),
        ),
        migrations.AlterField(
            model_name='log',
            name='create_time',
            field=models.DateTimeField(default=datetime.datetime(2016, 2, 9, 19, 7, 7, 928594)),
        ),
    ]