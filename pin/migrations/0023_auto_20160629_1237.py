# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0022_useractivitiessample_array'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlable',
            name='lable',
            field=models.TextField(),
        ),
    ]
