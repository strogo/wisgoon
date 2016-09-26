from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, SimpleStatement

isConnected = False
session = None


class CassandraModel():
    def __init__(self):
        global isConnected, session
        if not isConnected:
            cluster = Cluster(['127.0.0.1', '79.127.125.104', '79.127.125.99'])
            session = cluster.connect("wisgoon")
            isConnected = True


class PostStats(CassandraModel):
    post_id = None

    def __init__(self, post_id):
        CassandraModel.__init__(self)
        self.post_id = post_id

    def inc_view(self):
        sql = """UPDATE post_stats
                 SET cnt_view = cnt_view + 1
                 WHERE post_id={};"""\
            .format(self.post_id)
        session.execute_async(sql)

    def get_cnt_view(self):
        query = "SELECT cnt_view FROM post_stats where post_id={}"\
            .format(self.post_id)
        row = session.execute(query)
        if not row.current_rows:
            return 0
        return row[0].cnt_view


class UserStream(CassandraModel):
    def __init__(self):
        CassandraModel.__init__(self)

    def add_post(self, user_id, post_id, post_owner):
        query = """INSERT INTO user_stream
        (user_id, post_id , post_owner )
        VALUES ( {}, {}, {});""".format(user_id, post_id, post_owner)
        session.execute_async(query)

    def follow(self, user_id, post_id_list, post_owner):
        batch = BatchStatement()
        for pid in post_id_list:
            query = "INSERT INTO user_stream (user_id, post_id , post_owner ) VALUES (%s, %s, %s);"
            batch.add(SimpleStatement(query), (user_id, pid, post_owner))

        session.execute(batch)

    def unfollow(self, user_id, post_owner):
        query = """
        select post_id from user_stream WHERE user_id = {} and post_owner = {};
        """.format(user_id, post_owner)
        rows = session.execute(query)
        batch = BatchStatement()
        for r in rows:
            q = "DELETE from user_stream WHERE user_id = %s AND post_id = %s;"
            batch.add(SimpleStatement(q), (user_id, r.post_id))
        session.execute(batch)
