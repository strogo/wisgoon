# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0018_auto_20160628_1309'),
    ]

    operations = [
        migrations.AlterField(
            model_name='useractivitiessample',
            name='label',
            field=models.ForeignKey(related_name='lable', to='pin.Lable'),
        ),
    ]
