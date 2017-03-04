# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0047_auto_20170225_1254'),
    ]

    operations = [
        migrations.RenameField(
            model_name='phonedata',
            old_name='exrea_data',
            new_name='extra_data',
        ),
    ]
