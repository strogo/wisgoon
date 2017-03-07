# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0040_profile_invite_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='invite_code',
            field=models.CharField(db_index=True, max_length=255, null=True, blank=True),
        ),
    ]
