# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='KVStore',
            fields=[
                ('key', models.CharField(max_length=200, serialize=False, primary_key=True, db_column=b'key')),
                ('value', models.TextField()),
            ],
        ),
    ]
