# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_profile', '0030_profile_phone'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='jens',
            field=models.CharField(blank=True, max_length=2, null=True, choices=[(b'M', 'Male'), (b'F', 'Female')]),
        ),
    ]
