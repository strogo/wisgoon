# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pin', '0014_userlog_create_time'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserCron',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('due_date', models.DateTimeField(auto_now=True)),
                ('action', models.IntegerField(default=1, choices=[(1, 'ENABLE POST'), (2, 'DISABLE POST'), (3, 'ENABLE REPORT'), (4, 'DISABLE REPORT'), (5, 'ENABLE COMMENT'), (6, 'DISABLE COMMENT')])),
                ('after', models.IntegerField(default=1, choices=[(1, 'ENABLE POST'), (2, 'DISABLE POST'), (3, 'ENABLE REPORT'), (4, 'DISABLE REPORT'), (5, 'ENABLE COMMENT'), (6, 'DISABLE COMMENT')])),
                ('create_time', models.DateTimeField()),
                ('actor', models.ForeignKey(related_name='actor_cron', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(related_name='user_cron', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserPermissions',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post', models.BooleanField(default=True)),
                ('comment', models.BooleanField(default=True)),
                ('report', models.BooleanField(default=True)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='userlog',
            name='action',
            field=models.IntegerField(default=6, choices=[(1, 'BAN IMEI'), (2, 'DEBAN IMEI'), (3, 'BAN PROFILE'), (4, 'DEBAN PROFILE'), (5, 'DEACTIVE'), (6, 'ACTIVE'), (7, 'ENABLE POST'), (8, 'DISABLE POST'), (9, 'ENABLE REPORT'), (10, 'DISABLE REPORT'), (11, 'ENABLE COMMENT'), (12, 'DISABLE COMMENT')]),
        ),
    ]
