# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table(u'shop_category', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('text', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'shop', ['Category'])

        # Adding model 'Product'
        db.create_table(u'shop_product', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('price', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('in_stock', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Category'])),
        ))
        db.send_create_signal(u'shop', ['Product'])

        # Adding model 'ProductImages'
        db.create_table(u'shop_productimages', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('product', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['shop.Product'])),
        ))
        db.send_create_signal(u'shop', ['ProductImages'])


    def backwards(self, orm):
        # Deleting model 'Category'
        db.delete_table(u'shop_category')

        # Deleting model 'Product'
        db.delete_table(u'shop_product')

        # Deleting model 'ProductImages'
        db.delete_table(u'shop_productimages')


    models = {
        u'shop.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'text': ('django.db.models.fields.TextField', [], {})
        },
        u'shop.product': {
            'Meta': {'object_name': 'Product'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shop.Category']"}),
            'description': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'in_stock': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'shop.productimages': {
            'Meta': {'object_name': 'ProductImages'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shop.Product']"})
        }
    }

    complete_apps = ['shop']