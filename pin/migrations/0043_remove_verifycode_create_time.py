# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0042_verifycode_create_at'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='verifycode',
            name='create_time',
        ),
    ]
