# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0023_auto_20160629_1237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlable',
            name='lable',
            field=models.TextField(null=True, blank=True),
        ),
    ]
