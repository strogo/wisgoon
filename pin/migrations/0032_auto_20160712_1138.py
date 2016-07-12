# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0031_campaign_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='campaign',
            name='title',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
