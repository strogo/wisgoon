# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Category'
        db.create_table('rss_category', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('en_title', self.gf('django.db.models.fields.CharField')(max_length=1000)),
            ('image', self.gf('django.db.models.fields.files.ImageField')(max_length=100)),
            ('order', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('rss', ['Category'])

        # Adding model 'Feed'
        db.create_table('rss_feed', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=1000, blank=True)),
            ('last_fetch', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('priority', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('creator', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('followers', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('view', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('status', self.gf('django.db.models.fields.IntegerField')(default=1)),
            ('lock', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('category', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['rss.Category'], null=True, blank=True)),
        ))
        db.send_create_signal('rss', ['Feed'])

        # Adding model 'Item'
        db.create_table('rss_item', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('title', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('description', self.gf('django.db.models.fields.TextField')()),
            ('url', self.gf('django.db.models.fields.URLField')(max_length=200)),
            ('url_crc', self.gf('django.db.models.fields.IntegerField')()),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('timestamp', self.gf('django.db.models.fields.IntegerField')(db_index=True)),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rss.Feed'])),
            ('image', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('goto', self.gf('django.db.models.fields.IntegerField')(default=0)),
            ('likes', self.gf('django.db.models.fields.IntegerField')(default=0)),
        ))
        db.send_create_signal('rss', ['Item'])

        # Adding unique constraint on 'Item', fields ['feed', 'url_crc']
        db.create_unique('rss_item', ['feed_id', 'url_crc'])

        # Adding model 'Subscribe'
        db.create_table('rss_subscribe', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('feed', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['rss.Feed'])),
        ))
        db.send_create_signal('rss', ['Subscribe'])

        # Adding unique constraint on 'Subscribe', fields ['feed', 'user']
        db.create_unique('rss_subscribe', ['feed_id', 'user_id'])

        # Adding model 'Likes'
        db.create_table('rss_likes', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='post_item', to=orm['rss.Item'])),
        ))
        db.send_create_signal('rss', ['Likes'])

        # Adding unique constraint on 'Likes', fields ['item', 'user']
        db.create_unique('rss_likes', ['item_id', 'user_id'])

        # Adding model 'Report'
        db.create_table('rss_report', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['auth.User'])),
            ('item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='report_item', to=orm['rss.Item'])),
            ('mode', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('rss', ['Report'])

        # Adding unique constraint on 'Report', fields ['item', 'user']
        db.create_unique('rss_report', ['item_id', 'user_id'])

        # Adding model 'Search'
        db.create_table('rss_search', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('keyword', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('slug', self.gf('django.db.models.fields.SlugField')(max_length=50)),
            ('accept', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('count', self.gf('django.db.models.fields.IntegerField')(default=1)),
        ))
        db.send_create_signal('rss', ['Search'])

        # Adding model 'Lastview'
        db.create_table('rss_lastview', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('item', self.gf('django.db.models.fields.IntegerField')(unique=True)),
        ))
        db.send_create_signal('rss', ['Lastview'])


    def backwards(self, orm):
        # Removing unique constraint on 'Report', fields ['item', 'user']
        db.delete_unique('rss_report', ['item_id', 'user_id'])

        # Removing unique constraint on 'Likes', fields ['item', 'user']
        db.delete_unique('rss_likes', ['item_id', 'user_id'])

        # Removing unique constraint on 'Subscribe', fields ['feed', 'user']
        db.delete_unique('rss_subscribe', ['feed_id', 'user_id'])

        # Removing unique constraint on 'Item', fields ['feed', 'url_crc']
        db.delete_unique('rss_item', ['feed_id', 'url_crc'])

        # Deleting model 'Category'
        db.delete_table('rss_category')

        # Deleting model 'Feed'
        db.delete_table('rss_feed')

        # Deleting model 'Item'
        db.delete_table('rss_item')

        # Deleting model 'Subscribe'
        db.delete_table('rss_subscribe')

        # Deleting model 'Likes'
        db.delete_table('rss_likes')

        # Deleting model 'Report'
        db.delete_table('rss_report')

        # Deleting model 'Search'
        db.delete_table('rss_search')

        # Deleting model 'Lastview'
        db.delete_table('rss_lastview')


    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        'rss.category': {
            'Meta': {'object_name': 'Category'},
            'en_title': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '1000'}),
            'order': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'rss.feed': {
            'Meta': {'object_name': 'Feed'},
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': "orm['rss.Category']", 'null': 'True', 'blank': 'True'}),
            'creator': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'followers': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_fetch': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'lock': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'priority': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '1000', 'blank': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'view': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        'rss.item': {
            'Meta': {'unique_together': "(('feed', 'url_crc'),)", 'object_name': 'Item'},
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            'description': ('django.db.models.fields.TextField', [], {}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rss.Feed']"}),
            'goto': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'likes': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'}),
            'url_crc': ('django.db.models.fields.IntegerField', [], {})
        },
        'rss.lastview': {
            'Meta': {'object_name': 'Lastview'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.IntegerField', [], {'unique': 'True'})
        },
        'rss.likes': {
            'Meta': {'unique_together': "(('item', 'user'),)", 'object_name': 'Likes'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'post_item'", 'to': "orm['rss.Item']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'rss.report': {
            'Meta': {'unique_together': "(('item', 'user'),)", 'object_name': 'Report'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'report_item'", 'to': "orm['rss.Item']"}),
            'mode': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'rss.search': {
            'Meta': {'object_name': 'Search'},
            'accept': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'count': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keyword': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'})
        },
        'rss.subscribe': {
            'Meta': {'unique_together': "(('feed', 'user'),)", 'object_name': 'Subscribe'},
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['rss.Feed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        }
    }

    complete_apps = ['rss']