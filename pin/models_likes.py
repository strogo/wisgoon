# from cassandra.cqlengine import columns
# from cassandra.cqlengine import connection
# from cassandra.cqlengine import management
# from datetime import datetime
# from cassandra.cqlengine.management import sync_table
# from cassandra.cqlengine.models import Model


# class LikesModel(Model):
#     post_id = columns.Integer(primary_key=True)
#     likers = columns.Set(columns.Integer, index=True)


# connection.setup(['127.0.0.1'], "cqlengine", protocol_version=3)
# management.create_keyspace("cqlengine", replication_factor=1, strategy_class="SimpleStrategy")
# sync_table(LikesModel)
