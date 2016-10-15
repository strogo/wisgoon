# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0036_followrequest'),
    ]

    operations = [
        migrations.CreateModel(
            name='CampaignWinners',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('winners', models.TextField(null=True, blank=True)),
                ('campaign', models.ForeignKey(to='pin.Campaign')),
            ],
        ),
    ]
