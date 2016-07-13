# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0032_auto_20160712_1138'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='systemstate',
            name='registration_open',
        ),
    ]
