# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0043_remove_verifycode_create_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='verifycode',
            name='create_at',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
