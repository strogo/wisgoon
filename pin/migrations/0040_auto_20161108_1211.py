# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0039_phonedata_exrea_data'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phonedata',
            name='exrea_data',
            field=models.TextField(null=True, blank=True),
        ),
    ]
