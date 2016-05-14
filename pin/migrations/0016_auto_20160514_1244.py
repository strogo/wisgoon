# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0015_auto_20160509_1006'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='cnt_post',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='subcategory',
            name='cnt_post',
            field=models.IntegerField(default=0),
        ),
    ]
