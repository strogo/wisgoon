# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0030_systemstate'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='title',
            field=models.TextField(null=True, blank=True),
        ),
    ]
