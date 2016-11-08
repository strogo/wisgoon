# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0038_campaignwinners_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='phonedata',
            name='exrea_data',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
