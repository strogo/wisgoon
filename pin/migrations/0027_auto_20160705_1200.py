# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import datetime
from django.conf import settings
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pin', '0026_auto_20160705_1049'),
    ]

    operations = [
        migrations.RenameField(
            model_name='winnerslist',
            old_name='Rank',
            new_name='rank',
        ),
        migrations.AddField(
            model_name='campaign',
            name='owner',
            field=models.ForeignKey(related_name='campaign_owner', default=1, to=settings.AUTH_USER_MODEL),
            preserve_default=False,
        ),
    ]
