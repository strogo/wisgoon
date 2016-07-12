# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0029_auto_20160705_1324'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('read_only', models.BooleanField(default=False)),
                ('registration_open', models.BooleanField(default=True)),
            ],
        ),
    ]
