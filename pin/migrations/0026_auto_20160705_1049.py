# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pin', '0025_auto_20160629_1509'),
    ]

    operations = [
        migrations.CreateModel(
            name='Campaign',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField(null=True, blank=True)),
                ('primary_tag', models.CharField(max_length=100, null=True, blank=True)),
                ('tags', models.TextField(null=True, blank=True)),
                ('is_current', models.BooleanField(default=False)),
                ('start_date', models.DateTimeField(null=True, blank=True)),
                ('end_date', models.DateTimeField(null=True, blank=True)),
                ('expired', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='WinnersList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.TextField(null=True, blank=True)),
                ('Rank', models.IntegerField(default=0)),
                ('campaign', models.ForeignKey(to='pin.Campaign')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='campaign',
            name='winners',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='pin.WinnersList'),
        ),
    ]
