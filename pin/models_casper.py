from django.conf import settings
from cassandra.cluster import Cluster
from cassandra.query import BatchStatement, SimpleStatement
import redis

isConnected = False
session = None

redis_server = redis.Redis(settings.REDIS_DB_2)


class CassandraModel():
    def __init__(self):
        global isConnected, session
        if not isConnected:
            if settings.DEVEL_BRANCH:
                cluster = Cluster(['79.127.125.104', '79.127.125.99'])
            elif settings.DEBUG:
                cluster = Cluster(['127.0.0.1'])
            else:
                cluster = Cluster(['79.127.125.104', '79.127.125.99'])
            session = cluster.connect("wisgoon")
            isConnected = True


class Notification(CassandraModel):
    def __init__(self):
        CassandraModel.__init__(self)

    def set_notif(self, a_user_id, a_type, a_actor,
                  a_object_id, a_date, comment=None):
        ttl = 30 * 86400
        status = True
        if not a_object_id:
            a_object_id = 0

        hash_str = "{}:{}:{}".format(a_actor, a_object_id, a_type)
        print a_type, "type"
        # if notif was not comment
        if a_type != 2:
            query = """
            SELECT date FROM notification
            where user_id = {} AND hash = '{}'
            """.format(a_user_id, hash_str)

            res = session.execute(query)

            # if exists row, remove row
            if res.current_rows:
                status = False
                date = res.current_rows[0].date
                self.remove_notif(a_user_id, date)
        else:
            a_object_id = int(comment.id)

        self.create_notif(a_user_id=a_user_id,
                          a_type=a_type,
                          a_actor=a_actor,
                          a_object_id=a_object_id,
                          a_date=a_date,
                          hash_str=hash_str,
                          ttl=ttl)
        return status

    def get_notif(self, a_user_id, older=None):
        if older:
            query = """
            SELECT * FROM notification
            WHERE user_id = {}
            AND date<{} AND deleted=False
            LIMIT 20""".format(a_user_id, older)
        else:
            query = """
            SELECT * FROM notification
            WHERE user_id = {} AND deleted=False
            LIMIT 20""".format(a_user_id)

        res = session.execute(query)
        return res

    def remove_notif(self, a_user_id, a_date):
        query = """
                DELETE FROM Notification
                where user_id={} and date={}
                """.format(a_user_id, a_date)
        session.execute(query)

    def create_notif(self, a_user_id, a_type,
                     a_actor, a_object_id, a_date,
                     hash_str, ttl):

        query = """INSERT INTO notification
        (user_id, date, actor, object_id, type, deleted, hash)
        VALUES
        ({}, {}, {}, {}, {}, {}, '{}') USING TTL {} ;"""\
            .format(a_user_id,
                    a_date,
                    a_actor,
                    a_object_id,
                    a_type,
                    False,
                    hash_str,
                    ttl)
        session.execute(query)

    # Set deleted field True
    def update_notif(self, a_user_id, a_type, a_actor, a_object_id):

        if not a_object_id:
            a_object_id = 0

        hash_str = "{}:{}:{}".format(a_actor, a_object_id, a_type)

        # if notif was not comment
        query = """
        SELECT date FROM notification
        where user_id = {} AND hash = '{}'
        """.format(a_user_id, hash_str)

        res = session.execute(query)

        # if exists row, remove row
        if res.current_rows:
            date = res.current_rows[0].date
            query = """UPDATE notification SET deleted=True
                    WHERE user_id={} and date={}"""\
                        .format(a_user_id, date)
        session.execute(query)

    def remove_comment_notif(self, a_user_id, comment_id):

        # hash_str = "{}:{}:{}".format(a_actor, a_object_id, a_type)

        # if notif was not comment
        query = """
        SELECT date FROM notification
        where user_id = {} AND object_id = {}
        """.format(a_user_id, comment_id)
        res = session.execute(query)

        # if exists row, remove row
        if res.current_rows:
            date = res.current_rows[0].date
            self.remove_notif(a_user_id, date)


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
        query = "SELECT cnt_view FROM post_stats WHERE post_id={}"\
            .format(self.post_id)
        row = session.execute(query)
        if not row.current_rows:
            return 0
        return row[0].cnt_view


class CatStreams(CassandraModel):
    LATEST_CAT = "latest"

    def __init__(self):
        CassandraModel.__init__(self)

    def get_cat_name(self, cat_id):
        return "cat_{}".format(cat_id)

    def add_to_latest(self, post_id, owner_id):
        query = """
        INSERT INTO streams (name, owner , post_id )
        VALUES ( '{}', {}, {});
        """.format(self.LATEST_CAT, owner_id, post_id)

        session.execute(query)

    def remove_from_latest(self, post_id):
        query = """
        DELETE FROM streams WHERE name='{}' AND post_id = {};
        """.format(self.LATEST_CAT, post_id)
        session.execute(query)

    def add_post(self, cat_id, post_id, owner_id, timestamp):
        cat_name = self.get_cat_name(cat_id)

        query = """
        INSERT INTO streams (name, owner , post_id )
        VALUES ( '{}', {}, {});
        """.format(cat_name, owner_id, post_id)

        session.execute(query)

        self.add_to_latest(post_id, owner_id)

    def remove_post(self, cat_id, post_id):
        cat_name = self.get_cat_name(cat_id)
        query = """
        DELETE FROM streams WHERE name='{}' AND post_id = {};
        """.format(cat_name, post_id)
        session.execute(query)

        self.remove_from_latest(post_id)

    def get_posts(self, cat_id, pid):
        if cat_id == 0:
            cat_name = self.LATEST_CAT
        else:
            cat_name = self.get_cat_name(cat_id)

        if pid == 0:
            query = """
            SELECT post_id FROM streams
            WHERE name='{}'
            LIMIT 20;
            """.format(cat_name)
        else:
            query = """
            SELECT post_id FROM streams
            WHERE name='{}' AND post_id < {}
            LIMIT 20;
            """.format(cat_name, pid)
        rows = session.execute(query)
        post_id_list = [int(p.post_id) for p in rows]

        return post_id_list


class UserStream(CassandraModel):
    def __init__(self):
        CassandraModel.__init__(self)

    def add_post(self, user_id, post_id, post_owner):
        query = """INSERT INTO user_stream
        (user_id, post_id , post_owner )
        VALUES ( {}, {}, {});""".format(user_id, post_id, post_owner)
        session.execute(query)

        key = "ltrim:user:{}".format(user_id)
        get_key = redis_server.get(key)
        if not get_key:
            # print "start ltrim user_id {}".format(user_id)
            self.ltrim(user_id)
            redis_server.set(key, 1, 3600)

    def ltrim(self, user_id, limit=1000):
        query = """
        select * from user_stream WHERE user_id = {} limit {};
        """.format(user_id, limit)
        rows = session.execute(query)
        last_post_id = None
        for r in rows:
            last_post_id = r.post_id

        if not last_post_id:
            return

        query = """
        select post_id from user_stream WHERE user_id = {} and post_id < {};
        """.format(user_id, last_post_id)
        rows = session.execute(query)
        cnt = 0
        batch = BatchStatement()
        for r in rows:
            cnt += 1
            q = "DELETE from user_stream WHERE user_id = %s AND post_id = %s;"
            batch.add(SimpleStatement(q), (user_id, r.post_id))
            if cnt == 1000:
                session.execute(batch)
                batch = BatchStatement()
                cnt = 0

        session.execute(batch)

    def follow(self, user_id, post_id_list, post_owner):
        batch = BatchStatement()
        for pid in post_id_list:
            query = """
            INSERT INTO user_stream (user_id, post_id , post_owner )
            VALUES (%s, %s, %s);"""
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

    def get_posts(self, user_id, pid):
        if pid == 0:
            query = """
            SELECT post_id FROM user_stream
            WHERE user_id = {}
            LIMIT 20;
            """.format(user_id)
        else:
            query = """
            SELECT post_id FROM user_stream
            WHERE user_id = {} AND post_id < {}
            LIMIT 20;
            """.format(user_id, pid)
        rows = session.execute(query)
        post_id_list = [int(p.post_id) for p in rows]

        return post_id_list
