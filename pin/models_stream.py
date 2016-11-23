import redis
from django.conf import settings
from pin.models_casper import UserStream

# stream server
ss = redis.Redis(settings.REDIS_DB_104)

# user stream production
stream_key = "us_p:{}"

stream_limit = 500


class RedisUserStream(object):
    def __init__(self):
        pass

    def migrate_user_stream(self, user_id):
        skey = stream_key.format(user_id)
        if not ss.exists(skey):
            us = UserStream()
            uslist = []
            for r in us.get_post_data(user_id, 0, stream_limit):
                post_hash = "{}:{}".format(r.post_id, r.post_owner)
                uslist.append(post_hash)

            uslist.reverse()
            sspipe = ss.pipeline()
            for ul in uslist:
                sspipe.lpush(skey, ul)
            sspipe.execute()

    def add_post(self, user_ids, post_id, post_owner):
        post_hash = "{}:{}".format(post_id, post_owner)
        for uid in user_ids:
            self.migrate_user_stream(uid)

        sspipe = ss.pipeline()
        for uid in user_ids:
            skey = stream_key.format(uid)
            sspipe.lpush(skey, post_hash)
            sspipe.ltrim(skey, 0, stream_limit - 1)
        sspipe.execute()

    def convert_posts(self, post_list):
        pass

    def get_stream_posts(self, user_id, pid=0, limit=20):
        skey = stream_key.format(user_id)
        self.migrate_user_stream(user_id)

        if pid == 0:
            pl = ss.lrange(skey, 0, limit - 1)
        else:
            pid_index = None
            key_stand = "{}:".format(pid)
            pl = ss.lrange(skey, 0, -1)
            for pid in pl:
                if key_stand in pid:
                    pid_index = pl.index(str(pid))
                    break
            if pid_index:
                pl = pl[pid_index + 1: pid_index + limit]
            else:
                return []

        idis = []
        for pid in pl:
            idis.append(pid.split(":")[0])

        return idis

    def get_posts(self, user_id, pid=0, limit=20, flat=False):
        skey = stream_key.format(user_id)
        self.migrate_user_stream(user_id)
        post_l = ss.lrange(skey, 0, limit)
        if flat:
            return post_l
        al = []
        for pl in post_l:
            post_id, post_owner = pl.split(":")
            # al.append({"post_id":int(post_id), "post_owner": int(post_owner)})
            al.append({int(post_id): int(post_owner)})
        return al

    def follow(self, user_id, post_list, post_owner):
        skey = stream_key.format(user_id)
        cur_posts = self.get_posts(post_owner, 0, -1)
        for p in post_list:
            if {int(p): int(post_owner)} not in cur_posts:
                cur_posts.append({int(p): int(post_owner)})
        cur_posts = sorted(cur_posts, reverse=True)
        al = []
        for cp in cur_posts:
            cpitem = cp.items()[0]
            newitem = "{}:{}".format(cpitem[0], cpitem[1])
            al.append(newitem)
        ss.delete(skey)
        al.reverse()
        if al:
            ss.lpush(skey, *al)
        ss.ltrim(skey, 0, stream_limit - 1)

    def unfollow(self, user_id, target_id):
        skey = stream_key.format(user_id)
        cur_posts = self.get_posts(user_id, 0, -1, True)
        key_stand = ":{}".format(target_id)
        sspipe = ss.pipeline()
        for p in cur_posts:
            if key_stand in p:
                sspipe.lrem(skey, p, 0)
        sspipe.execute()
