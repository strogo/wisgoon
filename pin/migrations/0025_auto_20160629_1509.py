# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0024_auto_20160629_1239'),
    ]

    operations = [
        migrations.RenameField(
            model_name='useractivitiessample',
            old_name='label',
            new_name='lable',
        ),
    ]
