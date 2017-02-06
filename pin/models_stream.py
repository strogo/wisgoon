import redis
# import calendar
# import datetime
import time

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

    def get_post_hash(self, post_id, post_owner):
        post_hash = "{}:{}".format(post_id, post_owner)
        return post_hash

    def get_post_dict(self, post_id, post_owner):
        d = {
            int(post_id): int(post_owner)
        }
        return d

    def migrate_user_stream(self, user_id):
        return
        skey = stream_key.format(user_id)
        if not ss.exists(skey):
            us = UserStream()
            uslist = []
            for r in us.get_post_data(user_id, 0, stream_limit):
                post_hash = self.get_post_hash(r.post_id, r.post_owner)
                uslist.append(post_hash)

            uslist.reverse()
            sspipe = ss.pipeline()
            for ul in uslist:
                sspipe.lpush(skey, ul)
            sspipe.execute()

    def add_post(self, user_ids, post_id, post_owner):
        post_hash = self.get_post_hash(post_id, post_owner)
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
            post_dict = self.get_post_dict(post_id, post_owner)
            al.append(post_dict)
        return al

    def follow(self, user_id, post_list, post_owner):
        skey = stream_key.format(user_id)
        cur_posts = self.get_posts(user_id, 0, -1)
        for p in post_list:
            post_dict = self.get_post_dict(p, post_owner)
            if post_dict not in cur_posts:
                cur_posts.append(post_dict)
        cur_posts = sorted(cur_posts, reverse=True)
        al = []
        for cp in cur_posts:
            cpitem = cp.items()[0]
            newitem = self.get_post_hash(cpitem[0], cpitem[1])
            al.append(newitem)
        sspipe = ss.pipeline()
        sspipe.delete(skey)
        al.reverse()
        if al:
            sspipe.lpush(skey, *al)
        sspipe.ltrim(skey, 0, stream_limit - 1)
        sspipe.execute()

    def unfollow(self, user_id, target_id):
        skey = stream_key.format(user_id)
        cur_posts = self.get_posts(user_id, 0, -1, True)
        key_stand = ":{}".format(target_id)
        sspipe = ss.pipeline()
        for p in cur_posts:
            if key_stand in p:
                sspipe.lrem(skey, p, 0)
        sspipe.execute()


class RedisTopPostStream(object):
    def __init__(self):
        pass

    def add_post(self, post_id, cnt_like, date):
        keys = self.get_keys(date)
        keys_list = ["top_last_month", "top_last_week",
                     "top_last_day", "top_today"]
        for key in keys:
            ss.zadd(key, post_id, cnt_like)

            # Remove from other stream
            keys_list.remove(key)
            self.remove_from_stream(keys=keys_list, value=post_id)
            if ss.zcard(key) > 1000:
                self.trim_stream(key)
        self.add_top_all_stream(post_id=post_id, cnt_like=cnt_like)

    def add_top_all_stream(self, post_id, cnt_like):
        key = 'top_all'
        ss.zadd(key, post_id, cnt_like)
        if ss.zcard(key) > 1000:
                self.trim_stream(key)

    def trim_stream(self, key):
        ss.zremrangebyrank(key, 0, 0)

    def remove_from_stream(self, keys, value):
        for key in keys:
            ss.zrem(key, value)

    def get_keys(self, date):
        from pin.api6.tools import timestamp_to_local_datetime
        keys = []

        dt_now = timestamp_to_local_datetime(int(time.time()))

        diff = dt_now - date
        days = abs(diff.days)

        # first_last_week = dt_now - datetime.timedelta(days=7)
        if 7 < days <= 30:
            keys.append("top_last_month")

        elif 1 < days <= 7:
            keys.append("top_last_week")

        elif days == 1:
            keys.append("top_last_day")

        elif days == 0:
            keys.append("top_today")

        return keys

    def get_posts(self, key, offset):
        if offset != 0:
            offset = offset + 1
        post_ids = ss.zrevrange(key, offset, offset + 20)
        return post_ids

    # def in_last_moth_range(self, cur_date, date):
    #     # if cur_date.month == 1:
    #     #     month = 12
    #     #     year = cur_date.year - 1
    #     # else:
    #     #     year = cur_date.year
    #     #     month = cur_date.month - 1
    #     # status = False

    #     # _, num_days = calendar.monthrange(year, month)
    #     # first_day = datetime.datetime(year, month, 1)
    #     # last_day = datetime.datetime(year, month, num_days, 23, 59)
    #     # if first_day <= date <= last_day:
    #     status = False
    #     diff = cur_date - date
    #     if 7 < abs(diff.days) <= 30:
    #         status = True
    #     return status

    # def in_last_day_range(self, cur_date, date):
    #     status = False
    #     # start = cur_date - datetime.timedelta(days=1)
    #     # start_day = start.replace(hour=0, minute=0, second=0)
    #     # end_day = start.replace(hour=23, minute=59, second=59)
    #     # if start_day <= date <= end_day:
    #     diff = cur_date - date
    #     if abs(diff.days) == 1:
    #         status = True
    #     return status

    # def in_today_range(self, cur_date, date):
    #     status = False
    #     # start_day = cur_date.replace(hour=0, minute=0, second=0)
    #     # end_day = cur_date.replace(hour=23, minute=59, second=59)
    #     # if start_day <= date <= end_day:
    #     diff = cur_date - date
    #     if abs(diff.days) > 0:
    #         status = True
    #     return status

    # def in_week_range(self, cur_date, date):
    #     status = False
    #     # start_day = cur_date.replace(hour=0, minute=0, second=0)
    #     # end_day = cur_date.replace(hour=23, minute=59, second=59)
    #     # if start_day <= date <= end_day:
    #     diff = cur_date - date
    #     if 1 < abs(diff.days) <= 7:
    #         status = True
    #     return status
