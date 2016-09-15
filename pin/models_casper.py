from cassandra.cluster import Cluster


cluster = Cluster(['127.0.0.1', '79.127.125.104', '79.127.125.99'])
session = cluster.connect("wisgoon")


class PostStats():
    post_id = None

    def __init__(self, post_id):
        self.post_id = post_id

    def inc_view(self):
        sql = "UPDATE post_stats SET cnt_view = cnt_view +1 WHERE post_id={};"\
            .format(self.post_id)
        session.execute_async(sql)

    def get_cnt_view(self):
        query = "SELECT cnt_view FROM post_stats where post_id={}"\
            .format(self.post_id)
        row = session.execute(query)
        if not row.current_rows:
            return 0
        return row[0].cnt_view
