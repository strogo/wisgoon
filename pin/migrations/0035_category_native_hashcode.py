# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0034_auto_20160713_1717'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='native_hashcode',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
