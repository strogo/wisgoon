# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0011_auto_20160420_1634'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log',
            name='action',
            field=models.IntegerField(default=1, db_index=True, choices=[(1, 'delete'), (2, 'pending'), (3, 'bad comment'), (4, 'bad post'), (5, 'ban imei'), (6, 'ban by admin'), (8, 'Deactive user'), (7, 'activated')]),
        ),
        migrations.AlterField(
            model_name='userhistory',
            name='user',
            field=models.OneToOneField(related_name='user_hiostory', to=settings.AUTH_USER_MODEL),
        ),
    ]
