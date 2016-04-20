# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0010_commitment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reportedpostreporters',
            name='report_type',
            field=models.ForeignKey(default=None, blank=True, to='pin.ReportTypes', null=True),
        ),
    ]
