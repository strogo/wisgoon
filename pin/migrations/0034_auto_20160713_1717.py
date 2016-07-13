# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0033_remove_systemstate_registration_open'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='systemstate',
            name='read_only',
        ),
        migrations.AddField(
            model_name='systemstate',
            name='writable',
            field=models.BooleanField(default=True),
        ),
    ]
