# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Cart',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=150)),
                ('text', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('quantity', models.IntegerField(default=1)),
                ('status', models.IntegerField(default=1, choices=[(1, '\u062f\u0631 \u062d\u0627\u0644 \u0628\u0631\u0631\u0633\u06cc'), (2, '\u062a\u0627\u06cc\u06cc\u062f \u0634\u062f'), (3, '\u062f\u0631 \u062d\u0627\u0644 \u0622\u0645\u0627\u062f\u0647 \u0633\u0627\u0632\u06cc'), (4, '\u0627\u0631\u0633\u0627\u0644 \u06af\u0631\u062f\u06cc\u062f'), (5, '\u0628\u0647 \u062f\u0633\u062a \u0645\u0634\u062a\u0631\u06cc \u0631\u0633\u06cc\u062f')])),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=250)),
                ('title_en', models.CharField(default=b'', max_length=250, blank=True)),
                ('description', models.TextField()),
                ('price', models.IntegerField(default=0)),
                ('in_stock', models.BooleanField(default=True)),
                ('mode', models.IntegerField(default=1, choices=[(1, b'normal'), (2, b'special')])),
                ('category', models.ForeignKey(to='shop.Category')),
            ],
        ),
        migrations.CreateModel(
            name='ProductImages',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(upload_to=b'product')),
                ('primary', models.BooleanField(default=False)),
                ('product', models.ForeignKey(related_name='images', to='shop.Product')),
            ],
        ),
        migrations.CreateModel(
            name='Recivers',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('full_name', models.CharField(max_length=300)),
                ('address', models.TextField()),
                ('phone', models.CharField(max_length=50)),
                ('postal_code', models.CharField(max_length=100, blank=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ForeignKey(to='shop.Product'),
        ),
        migrations.AddField(
            model_name='order',
            name='reciver',
            field=models.ForeignKey(to='shop.Recivers'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(to='shop.Product'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
