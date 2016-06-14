# from uuid import uuid1
import random
from cassandra.cqlengine import columns
from cassandra.cqlengine import connection
from cassandra.cqlengine import management
from cassandra.cqlengine.management import sync_table
from cassandra.cqlengine.models import Model


class LikesModel(Model):
    post_id = columns.Integer(primary_key=True)
    likers = columns.Set(columns.Integer, index=True)
    # time = columns.TimeUUID(primary_key=True, clustering_order="desc",
    #                         default=uuid1)
    # user = columns.Integer(primary_key=True, index=True)


connection.setup(['127.0.0.1'], "wisgoodbv000", protocol_version=3)
management.create_keyspace_simple("wisgoodbv000", replication_factor=1)

sync_table(LikesModel)


def get_rand():
    return random.randint(1, 20)

for i in range(1, 10):
    # LikesModel.create(post_id=1, likers=[1])
    LikesModel.objects(post_id=get_rand()).update(likers__add={get_rand()})
    # LikesModel.create(post_id=i % 2 + 1,
    # user=random.randint(1, 1000))
