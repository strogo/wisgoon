# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0027_auto_20160705_1200'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='notif',
            field=models.BooleanField(default=True),
        ),
    ]
