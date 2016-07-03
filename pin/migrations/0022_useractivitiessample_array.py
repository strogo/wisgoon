# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0021_userlable'),
    ]

    operations = [
        migrations.AddField(
            model_name='useractivitiessample',
            name='array',
            field=models.TextField(null=True, blank=True),
        ),
    ]
