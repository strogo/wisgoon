# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0037_auto_20170116_1234'),
    ]

    operations = [
        migrations.AlterField(
            model_name='package',
            name='day',
            field=models.IntegerField(default=0),
        ),
    ]
