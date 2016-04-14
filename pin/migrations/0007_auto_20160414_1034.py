# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pin', '0006_auto_20160414_1016'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportTypes',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('pririty', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='reportedpost',
            name='priority',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userhistory',
            name='priority',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='reportedpostreporters',
            name='report_type',
            field=models.ForeignKey(default=None, blank=True, to='pin.ReportTypes'),
        ),
    ]
