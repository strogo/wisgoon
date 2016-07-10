from django.core.management.base import BaseCommand
import redis
from django.conf import settings
from django.contrib.auth.models import User
from pin.models import UserActivities, UserActivitiesSample
from datetime import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):
        user_id = raw_input("Enter user id: ")
        print datetime.now(), "  1"
        redis_server = redis.Redis(settings.REDIS_DB_2, db=9)
        users = User.objects.only('id').filter(id=int(user_id))
        print datetime.now(), "  2"

        for user in users:
            like_cat_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            keys = redis_server.keys("cnt_like:user:{}:*".format(user.id))
            for key in keys:
                index = int(key.split(":")[-1]) - 1
                like_cat_list[index] = int(redis_server.get(key))

            print datetime.now(), "  3"
            user_activity, created = UserActivities.objects.get_or_create(user_id=user.id)
            if created:
                user_activity.create_at = datetime.now()
            user_activity.activities = like_cat_list
            user_activity.update_at = datetime.now()
            user_activity.save()
            print datetime.now(), "  4"
            print "create user {} like activity".format(user.id)
        print datetime.now(), "  5"

        # samples = UserActivitiesSample.objects.all()

        # for sample in samples:
        #     user_activities = sample.userlikeactivities_set.all()
        #     like_cat_sample_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        #                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        #                             0, 0]

        #     for user_activitie in user_activities:
        #         index = user_activitie.category_id - 1
        #         like_cat_sample_list[index] = int(user_activitie.score)

        #     max_lable = max(like_cat_sample_list)

        #     sample.array = like_cat_sample_list
        #     sample.lable_id = like_cat_sample_list.index(max_lable) + 1
        #     sample.save()
        #     print "prepare sample {}".format(sample.id)
