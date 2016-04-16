# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0007_auto_20160414_1034'),
    ]

    operations = [
        migrations.AddField(
            model_name='userhistory',
            name='admin_post_deleted',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userhistory',
            name='cnt_report',
            field=models.IntegerField(default=0),
        ),
    ]
