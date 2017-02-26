# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0045_auto_20170118_1553'),
    ]

    operations = [
        migrations.CreateModel(
            name='RemoveImage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('file', models.FileField(upload_to=b'pin/remove_file')),
            ],
        ),
    ]
