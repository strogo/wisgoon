# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0032_auto_20170111_1527'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='jens',
            field=models.CharField(default=b'M', max_length=2, null=True, blank=True, choices=[(b'M', 'Male'), (b'F', 'Female')]),
        ),
    ]
