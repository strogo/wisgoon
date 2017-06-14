# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0046_removeimage'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='removeimage',
            name='file',
        ),
        migrations.AddField(
            model_name='removeimage',
            name='status',
            field=models.IntegerField(default=0, choices=[(2, 'completed'), (1, 'in progress'), (0, 'pending')]),
        ),
        migrations.AddField(
            model_name='removeimage',
            name='text',
            field=models.TextField(default=''),
            preserve_default=False,
        ),
    ]
