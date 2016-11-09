# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0041_verifycode'),
    ]

    operations = [
        migrations.AddField(
            model_name='verifycode',
            name='create_at',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
