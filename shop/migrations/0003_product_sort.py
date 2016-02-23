# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0002_product_in_home'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='sort',
            field=models.IntegerField(default=0),
        ),
    ]
