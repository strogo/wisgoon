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


# connection.setup([settings.CASSANDRA_DB], "wisgoon", protocol_version=3)
# management.create_keyspace_simple("wisgoon", replication_factor=1)

# sync_table(PostStats)
# sync_table(UserLikedPostsOrder)
