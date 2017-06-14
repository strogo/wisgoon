# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0039_profile_rank'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='invite_code',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
    ]
