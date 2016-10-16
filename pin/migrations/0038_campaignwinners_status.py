# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0037_campaignwinners'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaignwinners',
            name='status',
            field=models.IntegerField(default=0, blank=True, verbose_name='Status', choices=[(2, 'completed'), (1, 'in progress'), (0, 'not calculate')]),
        ),
    ]
