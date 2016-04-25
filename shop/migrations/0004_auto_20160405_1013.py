# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0003_product_sort'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(default=1, choices=[(1, 'Pending'), (2, 'Accepted'), (3, 'Preparation'), (4, 'Sent'), (5, 'Recived')]),
        ),
        migrations.AlterField(
            model_name='product',
            name='mode',
            field=models.IntegerField(default=1, choices=[(1, b'normal'), (2, b'x2'), (3, b'H2'), (4, b'X2H2')]),
        ),
        migrations.AlterField(
            model_name='recivers',
            name='postal_code',
            field=models.CharField(max_length=100),
        ),
    ]
