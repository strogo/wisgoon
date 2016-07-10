from django.core.management.base import BaseCommand
import redis
from django.conf import settings
from django.contrib.auth.models import User
from pin.models import UserActivities, UserActivitiesSample
from datetime import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):
        redis_server = redis.Redis(settings.REDIS_DB_2, db=9)
        users = User.objects.values_list('id', flat=True).all()[:1000]
        print datetime.now()
        for user_id in users:
            like_cat_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            keys = redis_server.keys("cnt_like:user:{}:*".format(user_id))
            for key in keys:
                index = int(key.split(":")[-1]) - 1
                like_cat_list[index] = int(redis_server.get(key))

            user_activity = UserActivities.objects.filter(user_id=user_id)

            if user_activity.exists():
                user_activity.update(activities=like_cat_list, update_at=datetime.now())
            else:
                user_activity = UserActivities.objects\
                    .create(user_id=user_id, create_at=datetime.now(),
                            activities=like_cat_list, update_at=datetime.now())
            print "create user {} like activity".format(user_id)
        print datetime.now(), "\n////////////////////////////////////////\n"

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
