# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0028_campaign_notif'),
    ]

    operations = [
        migrations.AddField(
            model_name='campaign',
            name='award',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='help_text',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='campaign',
            name='logo',
            field=models.ImageField(default=b'', upload_to=b'pin/campaigns/'),
        ),
    ]
