# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0049_invitelog'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='limit',
            field=models.IntegerField(default=0),
        ),
    ]
