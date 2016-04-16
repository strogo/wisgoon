# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pin', '0005_auto_20160402_1700'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReportedPost',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cnt_report', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='ReportedPostReporters',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('create_time', models.DateTimeField(auto_now=True)),
                ('reported_post', models.ForeignKey(to='pin.ReportedPost')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserHistory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pos_report', models.IntegerField(default=0)),
                ('neg_report', models.IntegerField(default=0)),
                ('user', models.OneToOneField(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='reportedpost',
            name='post',
            field=models.OneToOneField(to='pin.Post'),
        ),
    ]
