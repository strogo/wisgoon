# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pin', '0012_auto_20160503_1721'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.TextField()),
                ('action', models.IntegerField(default=6, choices=[(1, 'BAN IMEI')])),
                ('actor', models.ForeignKey(related_name='actor_log', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='user_log', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
