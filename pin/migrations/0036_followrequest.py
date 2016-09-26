# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pin', '0035_category_native_hashcode'),
    ]

    operations = [
        migrations.CreateModel(
            name='FollowRequest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('target', models.ForeignKey(related_name='target', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='user_req', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
