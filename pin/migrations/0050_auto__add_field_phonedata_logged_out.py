# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'PhoneData.logged_out'
        db.add_column(u'pin_phonedata', 'logged_out',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'PhoneData.logged_out'
        db.delete_column(u'pin_phonedata', 'logged_out')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'pin.ad': {
            'Meta': {'object_name': 'Ad'},
            'ads_type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'cnt_view': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'end': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'ended': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '15'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owner'", 'null': 'True', 'to': u"orm['auth.User']"}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pin.Post']"}),
            'start': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pin.app_data': {
            'Meta': {'object_name': 'App_data'},
            'current': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'version': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'version_code': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'})
        },
        u'pin.bills2': {
            'Meta': {'object_name': 'Bills2'},
            'amount': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'trans_id': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pin.block': {
            'Meta': {'object_name': 'Block'},
            'blocked': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'blocked'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'blocker'", 'to': u"orm['auth.User']"})
        },
        u'pin.category': {
            'Meta': {'object_name': 'Category'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'default': "''", 'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sub_category'", 'null': 'True', 'to': u"orm['pin.SubCategory']"}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'pin.comments': {
            'Meta': {'object_name': 'Comments'},
            'comment': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '15', 'db_index': 'True'}),
            'is_public': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'object_pk': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_post'", 'to': u"orm['pin.Post']"}),
            'reported': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_sender'", 'to': u"orm['auth.User']"})
        },
        u'pin.comments_score': {
            'Meta': {'object_name': 'Comments_score'},
            'comment': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pin.Comments']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'comment_like_user'", 'to': u"orm['auth.User']"})
        },
        u'pin.follow': {
            'Meta': {'object_name': 'Follow'},
            'follower': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'follower'", 'to': u"orm['auth.User']"}),
            'following': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'following'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pin.instaaccount': {
            'Meta': {'object_name': 'InstaAccount'},
            'cat': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pin.Category']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'insta_id': ('django.db.models.fields.IntegerField', [], {}),
            'lc': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 6, 27, 0, 0)', 'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pin.likes': {
            'Meta': {'unique_together': "(('post', 'user'),)", 'object_name': 'Likes'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.IPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '15'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'post_item'", 'to': u"orm['pin.Post']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'pin_post_user_like'", 'to': u"orm['auth.User']"})
        },
        u'pin.log': {
            'Meta': {'object_name': 'Log'},
            'action': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'content_type': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'}),
            'create_time': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime(2015, 6, 27, 0, 0)', 'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip_address': ('django.db.models.fields.IPAddressField', [], {'default': "'127.0.0.1'", 'max_length': '15', 'db_index': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'owner': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'post_image': ('django.db.models.fields.CharField', [], {'max_length': '250', 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'default': "''", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pin.notif': {
            'Meta': {'object_name': 'Notif'},
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pin.Post']"}),
            'seen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user_id'", 'to': u"orm['auth.User']"})
        },
        u'pin.notif_actors': {
            'Meta': {'object_name': 'Notif_actors'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actor'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'notif': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'notif'", 'to': u"orm['pin.Notif']"})
        },
        u'pin.notifbar': {
            'Meta': {'object_name': 'Notifbar'},
            'actor': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'actor_id'", 'to': u"orm['auth.User']"}),
            'date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pin.Post']"}),
            'seen': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'type': ('django.db.models.fields.IntegerField', [], {'default': '1'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'post_user_id'", 'to': u"orm['auth.User']"})
        },
        u'pin.official': {
            'Meta': {'object_name': 'Official'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mode': ('django.db.models.fields.IntegerField', [], {'default': "'1'"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        },
        u'pin.packages': {
            'Meta': {'object_name': 'Packages'},
            'icon': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'price': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'wis': ('django.db.models.fields.IntegerField', [], {'default': '0'})
        },
        u'pin.phonedata': {
            'Meta': {'object_name': 'PhoneData'},
            'android_version': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'app_version': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'google_token': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'imei': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'logged_out': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'os': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone_model': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone_serial': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'phone'", 'null': 'True', 'to': u"orm['auth.User']"})
        },
        u'pin.post': {
            'Meta': {'object_name': 'Post'},
            'actions': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'category': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['pin.Category']"}),
            'cnt_comment': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'blank': 'True'}),
            'cnt_like': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'create': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'create_date': ('django.db.models.fields.DateField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'device': ('django.db.models.fields.IntegerField', [], {'default': '1', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '32', 'blank': 'True'}),
            'height': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.CharField', [], {'max_length': '500'}),
            'is_ads': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'like': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'report': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'show_in_default': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'db_index': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'timestamp': ('django.db.models.fields.IntegerField', [], {'default': '1347546432', 'db_index': 'True'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '2000', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"}),
            'view': ('django.db.models.fields.IntegerField', [], {'default': '0', 'db_index': 'True'}),
            'width': ('django.db.models.fields.IntegerField', [], {'default': '-1', 'blank': 'True'})
        },
        u'pin.postmetadata': {
            'Meta': {'object_name': 'PostMetaData'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'img_236': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'img_236_h': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'img_500': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'img_500_h': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'original_size': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'post': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pin.Post']", 'unique': 'True'}),
            'status': ('django.db.models.fields.IntegerField', [], {'default': '1', 'db_index': 'True'})
        },
        u'pin.report': {
            'Meta': {'unique_together': "(('post', 'user'),)", 'object_name': 'Report'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'report_post'", 'to': u"orm['pin.Post']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'report_user'", 'to': u"orm['auth.User']"})
        },
        u'pin.sim': {
            'Meta': {'object_name': 'Sim'},
            'features': ('django.db.models.fields.TextField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['pin.Post']", 'unique': 'True'})
        },
        u'pin.stream': {
            'Meta': {'unique_together': "(('following', 'user', 'post'),)", 'object_name': 'Stream'},
            'date': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'following': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'stream_following'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'post': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pin.Post']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'user'", 'to': u"orm['auth.User']"})
        },
        u'pin.subcategory': {
            'Meta': {'object_name': 'SubCategory'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '250'})
        },
        u'taggit.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '100'}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '100'})
        },
        u'taggit.taggeditem': {
            'Meta': {'object_name': 'TaggedItem'},
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_tagged_items'", 'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'tag': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "u'taggit_taggeditem_items'", 'to': u"orm['taggit.Tag']"})
        }
    }

    complete_apps = ['pin']