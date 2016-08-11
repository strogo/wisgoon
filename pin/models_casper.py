# from uuid import uuid1
from django.conf import settings
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine import management
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model


class PostStats(Model):
    post_id = columns.Integer(primary_key=True)
    cnt_view = columns.Counter()


class PostComments(Model):
    post_id = columns.Integer(primary_key=True)
    create_time = columns.Integer(primary_key=True, clustering_order="desc")
    ip_address = columns.Text()
    comment = columns.Text()
    user_id = columns.Integer()
    old_comment_id = columns.Integer(index=True)


class PostData(Model):
    post_id = columns.Integer(primary_key=True)
    creator_ip = columns.Inet()
    create_time = columns.DateTime()


class UserStream(Model):
    user_id = columns.Integer(primary_key=True)
    post_id = columns.Integer(primary_key=True, clustering_order="desc")
    post_owner = columns.Integer(index=True)


# class UserLikedPosts(Model):
    # post_id = columns.Integer(primary_key=True)
    # user_id = columns.Integer(primary_key=True)

    # time = columns.TimeUUID(primary_key=True, clustering_order="desc",
    #                         default=uuid1)
    # user = columns.Integer(primary_key=True, index=True)


# class UserLikedPostsOrder(Model):
#     post_id = columns.Integer(primary_key=True)
#     like_time = columns.Integer(primary_key=True, clustering_order="desc")
#     user_id = columns.Integer(primary_key=True)

try:
    connection.setup([settings.CASSANDRA_DB], "wisgoon", protocol_version=3)
    management.create_keyspace_simple("wisgoon", replication_factor=1)

    sync_table(PostStats)
    sync_table(PostData)
    sync_table(UserStream)
except Exception, e:
    print str(e)
