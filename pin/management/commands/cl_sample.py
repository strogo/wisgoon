from django.core.management.base import BaseCommand
from pin.models import Category, UserActivitiesSample, Lable, UserActivities
import random
from django.contrib.auth.models import User
from datetime import datetime


class Command(BaseCommand):
    def handle(self, *args, **options):

        # add_lable = raw_input("Do you want to add lable y/n?")

        # if add_lable == 'y' or add_lable == '':
        #     lable_list = raw_input("Enter your lable. seprate with ','")
        #     create_lable(lables=lable_list)

        count_sample = raw_input("How many sample you want to add?")
        create_sample(count_sample)

        # count_activity = raw_input("How many user activity you want to add?")
        create_user_activity()


def create_lable(lables=[]):
    if lables:
        lable_list = lables.split(',')
        for lable in lable_list:
            Lable.objects.get_or_create(text=lable)
            print "lable {} was created".format(lable)
    else:
        categories = Category.objects.all()
        for cat in categories:
            Lable.objects.get_or_create(text=cat.title)
            print "lable {} was created".format(cat.title)


def create_sample(count_sample):
    lable_ids = Lable.objects.values_list('id', flat=True).order_by('id')

    for i in range(1, int(count_sample)):
        sample = UserActivitiesSample()
        sample.lable_id = random.randint(lable_ids[0], lable_ids[43])
        sample.save()

        for a in range(1, random.randint(2, 45)):
            sample.userlikeactivities_set\
                .create(score=random.randint(1, 10),
                        category_id=a,
                        user_activity=sample.id)
        print "sample {} was created".format(sample.id)


def create_user_activity(number=0):
    users = User.objects.values_list('id', flat=True).all()
    if number == 0:
        number = len(users)
    for user_id in users[:int(number)]:
        like_cat_list = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                         0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for a in range(1, random.randint(2, 44)):
            like_cat_list[a] = random.randint(1, 10)

        user_activity, created = UserActivities.objects.get_or_create(user_id=user_id)

        if created:
            user_activity.create_at = datetime.now()
        user_activity.activities = like_cat_list
        user_activity.update_at = datetime.now()
        user_activity.save()
        print "create user {} like activity".format(user_id)
