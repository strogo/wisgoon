from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine import management
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model


class LikesModel(Model):
    post_id = columns.Integer(primary_key=True)
    user = columns.Integer(primary_key=True)
    time = columns.Integer(index=True)


connection.setup(['127.0.0.1'], "wisgoodbv2", protocol_version=3)
management.create_keyspace_simple("wisgoodbv2", replication_factor=1)

sync_table(LikesModel)
