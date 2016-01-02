# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ProductImages.primary'
        db.add_column(u'shop_productimages', 'primary',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ProductImages.primary'
        db.delete_column(u'shop_productimages', 'primary')


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
            'mode': ('django.db.models.fields.IntegerField', [], {'default': '1', 'max_length': '30'}),
            'price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'title_en': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '250', 'blank': 'True'})
        },
        u'shop.productimages': {
            'Meta': {'object_name': 'ProductImages'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'primary': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'product': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['shop.Product']"})
        }
    }

    complete_apps = ['shop']